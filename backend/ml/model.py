import torch
import torch.nn as nn
import torchvision.models as models


class DogBreedClassifierModel(nn.Module):
    """
    Lightweight classification model targeting dog breed detection.
    Wraps MobileNetV3-Large backbone with a customized classification layer.
    """

    def __init__(self, num_classes: int) -> None:
        super().__init__()
        # Retrieve pretrained MobileNetV3-Large weights
        weights = models.MobileNet_V3_Large_Weights.DEFAULT
        self.backbone = models.mobilenet_v3_large(weights=weights)

        # Inspect final classifier input dimension
        # MobileNetV3-Large final block classifier is a Sequential layer where final projection is index 3
        in_features = self.backbone.classifier[3].in_features

        # Replace classification projection to map to combined breed count
        self.backbone.classifier[3] = nn.Linear(
            in_features=in_features, out_features=num_classes
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Executes forward tensor pass.
        """
        return self.backbone(x)
