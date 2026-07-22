import argparse
import json
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from ml.model import DogBreedClassifierModel

# ImageNet normalization statistics
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def get_data_loaders(
    data_dir: str, batch_size: int
) -> tuple[DataLoader, DataLoader, list[str]]:
    """
    Returns PyTorch DataLoaders and class breed names list.
    """
    train_transforms = transforms.Compose(
        [
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(
                brightness=0.1, contrast=0.1, saturation=0.1
            ),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ]
    )

    val_transforms = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD),
        ]
    )

    train_dataset = datasets.ImageFolder(
        root=os.path.join(data_dir, "train"), transform=train_transforms
    )
    val_dataset = datasets.ImageFolder(
        root=os.path.join(data_dir, "val"), transform=val_transforms
    )

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=0
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )

    return train_loader, val_loader, train_dataset.classes


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    lr: float,
    device: torch.device,
) -> nn.Module:
    """
    Standard training and validation run loop.
    """
    # CrossEntropy Loss with Label Smoothing for robustness
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_acc = 0.0
    best_weights = model.state_dict().copy()

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

        scheduler.step()
        epoch_loss = running_loss / total
        epoch_acc = correct / total

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * inputs.size(0)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()

        epoch_val_loss = val_loss / val_total
        epoch_val_acc = val_correct / val_total

        print(
            f"Epoch [{epoch + 1}/{epochs}] "
            f"Train Loss: {epoch_loss:.4f} | Train Acc: {epoch_acc:.4f} | "
            f"Val Loss: {epoch_val_loss:.4f} | Val Acc: {epoch_val_acc:.4f}"
        )

        if epoch_val_acc >= best_acc:
            best_acc = epoch_val_acc
            best_weights = model.state_dict().copy()

    print(f"Training completed. Best Validation Accuracy: {best_acc:.4f}")
    model.load_state_dict(best_weights)
    return model


def export_to_onnx(
    model: nn.Module, export_path: str, device: torch.device
) -> None:
    """
    Exports a trained PyTorch module model structure to ONNX.
    """
    model.eval()
    # Dummy input representing batch size 1, 3 channels, 224x224 image
    dummy_input = torch.randn(1, 3, 224, 224, device=device)

    print(f"Exporting model to ONNX format at: {export_path}...")
    torch.onnx.export(
        model,
        dummy_input,
        export_path,
        export_params=True,
        opset_version=15,  # Robust opset version
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={
            "input": {0: "batch_size"},  # allow variable batch sizes
            "output": {0: "batch_size"},
        },
    )
    print("ONNX export complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Training and exporting pipeline for Dog Breed Classification"
    )
    parser.add_argument(
        "--data-dir", default="./ml/dataset", help="Dataset root folder"
    )
    parser.add_argument(
        "--epochs", type=int, default=10, help="Number of training epochs"
    )
    parser.add_argument(
        "--batch-size", type=int, default=16, help="Minibatch size"
    )
    parser.add_argument(
        "--lr", type=float, default=1e-3, help="Optimizer learning rate"
    )
    parser.add_argument(
        "--onnx-path",
        default="./src/services/dog_breed_mobilenet.onnx",
        help="Target ONNX export file path",
    )
    parser.add_argument(
        "--labels-path",
        default="./src/services/dog_breeds.json",
        help="Target JSON index-to-labels mapping path",
    )
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running pipeline on hardware device: {device}")

    # Generate directories
    os.makedirs(os.path.dirname(args.onnx_path), exist_ok=True)
    os.makedirs(os.path.dirname(args.labels_path), exist_ok=True)

    # 1. Fetch Dataloaders
    train_loader, val_loader, classes = get_data_loaders(
        args.data_dir, args.batch_size
    )
    print(f"Loaded {len(classes)} classes: {classes}")

    # Save classes mapping file for production API server mapping lookup
    with open(args.labels_path, "w") as f:
        json.dump(classes, f, indent=2)
    print(f"Saved breed categories label mapping file to {args.labels_path}")

    # 2. Build model instance
    model = DogBreedClassifierModel(num_classes=len(classes)).to(device)

    # 3. Execute training
    trained_model = train_model(
        model, train_loader, val_loader, args.epochs, args.lr, device
    )

    # 4. Export graph structure
    export_to_onnx(trained_model, args.onnx_path, device)


if __name__ == "__main__":
    main()
