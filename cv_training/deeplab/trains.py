import argparse
import os
import numpy as np
from PIL import Image, ImageDraw

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from tqdm import tqdm


def resolve_path(base, p):
    return os.path.normpath(p) if os.path.isabs(p) else os.path.normpath(os.path.join(base, p))

class PolygonSegDataset(Dataset):
    """
    Dataset for polygon-based segmentation labels stored as TXT files.
    每行格式: class_id x1 y1 x2 y2 ... (归一化坐标)
    """
    def __init__(self, image_paths, basenames, mask_dir, img_size=(520,520)):
        assert len(image_paths) == len(basenames)
        self.image_paths = image_paths
        self.basenames = basenames
        self.mask_dir = mask_dir
        self.img_size = img_size

        self.img_trans = transforms.Compose([
            transforms.Resize(img_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
        ])

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        W, H = image.size
        mask_img = Image.new('L', (W, H), 0)
        draw = ImageDraw.Draw(mask_img)
        txt_path = os.path.join(self.mask_dir, self.basenames[idx] + '.txt')
        with open(txt_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                cls = int(parts[0]); coords = list(map(float, parts[1:]))
                pts = [(coords[i]*W, coords[i+1]*H) for i in range(0, len(coords), 2)]
                draw.polygon(pts, outline=cls, fill=cls)
        image = self.img_trans(image)
        mask = np.array(mask_img, dtype=np.int64)
        mask = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0).float()
        mask = nn.functional.interpolate(mask, size=self.img_size, mode='nearest').long().squeeze(0).squeeze(0)
        return image, mask


def get_dataloaders(image_paths, basenames, mask_dir,
                    batch_size=8, val_frac=0.2, num_workers=4):
    ds = PolygonSegDataset(image_paths, basenames, mask_dir)
    n = len(ds)
    n_val = int(n * val_frac)
    train_ds, val_ds = random_split(ds, [n - n_val, n_val])
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return train_loader, val_loader


def build_model(num_classes, device):
    weights = models.segmentation.DeepLabV3_ResNet50_Weights.COCO_WITH_VOC_LABELS_V1
    model = models.segmentation.deeplabv3_resnet50(weights=weights)
    model.classifier = models.segmentation.deeplabv3.DeepLabHead(2048, num_classes)
    return model.to(device)


def compute_metrics(preds, labels, num_classes):
    # preds, labels: flattened 1D tensors
    mask = (labels >= 0) & (labels < num_classes)
    hist = torch.bincount(
        num_classes * labels[mask] + preds[mask],
        minlength=num_classes**2
    ).reshape(num_classes, num_classes).float()
    # IoU for each class: TP / (TP + FP + FN)
    tp = torch.diag(hist)
    fp = hist.sum(0) - tp
    fn = hist.sum(1) - tp
    iu = tp / (tp + fp + fn + 1e-6)
    mean_iou = iu.mean().item()
    # pixel accuracy
    acc = tp.sum() / hist.sum()
    return mean_iou, acc.item()


def train_one_epoch(model, loader, criterion, optimizer, device, epoch, log_interval=10):
    model.train(); running_loss = 0.0
    pbar = tqdm(enumerate(loader), total=len(loader), desc=f"Epoch {epoch} [Train]")
    for batch_idx, (images, masks) in pbar:
        images, masks = images.to(device), masks.to(device)
        outputs = model(images)['out']
        loss = criterion(outputs, masks)
        optimizer.zero_grad(); loss.backward(); optimizer.step()
        running_loss += loss.item() * images.size(0)
        if (batch_idx+1) % log_interval == 0:
            avg = running_loss / ((batch_idx+1) * loader.batch_size)
            pbar.set_postfix({'batch_loss': f"{loss.item():.4f}", 'avg_loss': f"{avg:.4f}"})
    epoch_loss = running_loss / len(loader.dataset)
    return epoch_loss


def validate(model, loader, criterion, device, epoch, num_classes):
    model.eval(); running_loss = 0.0
    conf_preds = []
    conf_labels = []
    pbar = tqdm(loader, total=len(loader), desc=f"Epoch {epoch} [Val]  ")
    with torch.no_grad():
        for images, masks in pbar:
            images, masks = images.to(device), masks.to(device)
            outputs = model(images)['out']
            loss = criterion(outputs, masks)
            running_loss += loss.item() * images.size(0)
            preds = outputs.argmax(1)
            conf_preds.append(preds.flatten())
            conf_labels.append(masks.flatten())
            pbar.set_postfix({'val_loss': f"{loss.item():.4f}"})
    # concat all
    all_preds = torch.cat(conf_preds)
    all_labels = torch.cat(conf_labels)
    mean_iou, pix_acc = compute_metrics(all_preds.cpu(), all_labels.cpu(), num_classes)
    avg_loss = running_loss / len(loader.dataset)
    return avg_loss, mean_iou, pix_acc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-root',  type=str, required=False, default='C:/Users/lchna/Desktop/deeplab')
    parser.add_argument('--list-file',  type=str, default='Train.txt')
    parser.add_argument('--mask-dir',   type=str, default='data/labels/Train')
    parser.add_argument('--batch-size', type=int, default=8)
    parser.add_argument('--epochs',     type=int, default=25)
    parser.add_argument('--lr',         type=float, default=1e-4)
    parser.add_argument('--num-classes',type=int, default=21)
    parser.add_argument('--save-dir',   type=str, default='./checkpoints')
    parser.add_argument('--device',     type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--log-interval', type=int, default=10)
    args = parser.parse_args()

    root = os.path.normpath(args.data_root)
    list_f = resolve_path(root, args.list_file)
    mask_dir = resolve_path(root, args.mask_dir)

    with open(list_f) as f:
        rel_paths = [ln.strip() for ln in f if ln.strip()]
    image_paths = [resolve_path(root, p) for p in rel_paths]
    basenames = [os.path.splitext(os.path.basename(p))[0] for p in rel_paths]

    os.makedirs(args.save_dir, exist_ok=True)
    train_loader, val_loader = get_dataloaders(
        image_paths, basenames, mask_dir,
        batch_size=args.batch_size)

    model = build_model(args.num_classes, args.device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    best_iou = 0.0
    for ep in range(1, args.epochs+1):
        tr_loss = train_one_epoch(model, train_loader, criterion, optimizer,
                                  args.device, ep, args.log_interval)
        val_loss, miou, acc = validate(model, val_loader, criterion,
                                        args.device, ep, args.num_classes)
        print(f"Epoch {ep}/{args.epochs} — Train Loss: {tr_loss:.4f} | Val Loss: {val_loss:.4f} | mIoU: {miou:.4f} | PixAcc: {acc:.4f}")
        if miou > best_iou:
            best_iou = miou
            fp = os.path.join(args.save_dir, f'best_ep{ep}.pth')
            torch.save(model.state_dict(), fp)
            print(f"Saved best model by mIoU to {fp}")

if __name__ == '__main__':
    main()
