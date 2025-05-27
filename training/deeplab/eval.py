# eval_all.py

import os
import torch
import torch.nn as nn
from trains import resolve_path, PolygonSegDataset, validate, build_model
import torch
import matplotlib.pyplot as plt
from torchvision.utils import make_grid
import numpy as np

def main():
    data_root  = r"C:/Users/lchna/Desktop/deeplab"
    list_file  = os.path.join(data_root, "Train.txt")
    mask_dir   = os.path.join(data_root, "data/labels/Train")
    checkpoint = r"C:/Users/lchna/Desktop/deeplab/checkpoints/best_ep24.pth"
    device     = "cuda" if torch.cuda.is_available() else 'cpu'
    num_classes= 21
    batch_size = 8

    with open(list_file) as f:
        rels = [ln.strip() for ln in f if ln.strip()]
    img_paths = [resolve_path(data_root, p) for p in rels]
    basenames = [os.path.splitext(os.path.basename(p))[0] for p in rels]

    ds = PolygonSegDataset(img_paths, basenames, mask_dir)
    loader = torch.utils.data.DataLoader(
        ds, batch_size=batch_size, shuffle=False, num_workers=4
    )

    model = build_model(num_classes, device)
    model.load_state_dict(torch.load(checkpoint, map_location=device))
    model.to(device)

    # validate() 接受任何长度的 loader
    val_loss, miou, pix_acc = validate(
        model, loader, nn.CrossEntropyLoss(),
        device, epoch=0, num_classes=num_classes
    )
    visualize_segmentation(model, loader, device, num_samples=4)
    print(f"\nEvaluate All — Loss: {val_loss:.4f} | mIoU: {miou:.4f} | PixAcc: {pix_acc:.4f}")

def visualize_segmentation(model, loader, device, num_samples=4):
    model.eval()
    images, masks = next(iter(loader))  # 取第一 batch
    images = images.to(device)
    with torch.no_grad():
        outputs = model(images)['out']
        preds = outputs.argmax(1).cpu().numpy()  # (B, H, W)

    imgs_np = images.cpu().permute(0,2,3,1).numpy()  # (B,H,W,3), 已经 normalize 过

    # 反 normalize
    mean = np.array([0.485,0.456,0.406])
    std  = np.array([0.229,0.224,0.225])
    imgs_np = np.clip(imgs_np * std + mean, 0, 1)

    fig, axes = plt.subplots(num_samples, 3, figsize=(12, 4*num_samples))
    for i in range(num_samples):
        ax_img, ax_gt, ax_pred = axes[i]
        ax_img.imshow(imgs_np[i])
        ax_img.set_title('原图')
        ax_img.axis('off')

        ax_gt.imshow(imgs_np[i])
        ax_gt.imshow(masks[i].numpy(), alpha=0.5, cmap='jet')
        ax_gt.set_title('真值 Mask')
        ax_gt.axis('off')

        ax_pred.imshow(imgs_np[i])
        ax_pred.imshow(preds[i], alpha=0.5, cmap='jet')
        ax_pred.set_title('预测 Mask')
        ax_pred.axis('off')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
