import torch
import torchvision.transforms as transforms
from torchvision import datasets
import matplotlib.pyplot as plt
import albumentations as A
from albumentations.pytorch import ToTensorV2



class Cifar_10(datasets.CIFAR10):
    def __init__(self, root="./data", train=True, download=True, transform=None):
        super().__init__(root=root, train=train, download=download, transform=transform)

    def __getitem__(self, index):
        image, label = self.data[index], self.targets[index]

        if self.transform is not None:
            transformed = self.transform(image=image)
            image = transformed["image"]

        return image, label




def load_data(data_dir='./data'):
  batch_size = 512
  # Train data transformations

  train_transforms = A.Compose(
    [
        A.HorizontalFlip(p=0.1),
        A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=15, p=0.5),
        A.CoarseDropout (max_holes = 1, max_height=16, max_width=16, min_holes = 1, min_height=16, min_width=16, fill_value=.45, mask_fill_value = None),
        A.RGBShift(r_shift_limit=10, g_shift_limit=10, b_shift_limit=15, p=0.4),
        A.RandomBrightnessContrast(p=0.5),
        A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
        ToTensorV2()
    ])
  # Test data transformations
  test_transforms = A.Compose(
    [
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2()
    ])
 




  train_data = Cifar_10('../data', train=True, download=True, transform=train_transforms)
  test_data = Cifar_10('../data', train=False, download=True, transform=test_transforms)
  classes = ['plane', 'car', 'bird', 'cat','deer', 'dog', 'frog', 'horse', 'ship', 'truck']
  batch_size = 64

  kwargs = {'batch_size': batch_size, 'shuffle': True, 'num_workers': 2, 'pin_memory': True}

  test_loader = torch.utils.data.DataLoader(test_data, **kwargs)
  train_loader = torch.utils.data.DataLoader(train_data, **kwargs)
  train_loader = torch.utils.data.DataLoader(train_data, **kwargs)
  test_loader = torch.utils.data.DataLoader(test_data, **kwargs)
  return train_loader, test_loader





def visualise_input(train_loader):
  batch_data, batch_label = next(iter(train_loader))
  fig = plt.figure()
  for i in range(12):
    plt.subplot(3,4,i+1)
    plt.tight_layout()
    plt.imshow(batch_data[i].squeeze(0), cmap='gray')
    plt.title(batch_label[i].item())
    plt.xticks([])
    plt.yticks([])




from tqdm import tqdm

from tqdm import tqdm
# Data to plot accuracy and loss graphs
train_losses = []
test_losses = []
train_acc = []
test_acc = []

def train(model, device, train_loader, optimizer, epoch):
  model.train()
  pbar = tqdm(train_loader)

  train_loss = 0

  correct = 0
  processed = 0

  for batch_idx, (data, target) in enumerate(pbar):
    # get samples
    data, target = data.to(device), target.to(device)

    # Initfloat32
    optimizer.zero_grad()
    # In PyTorch, we need to set the gradients to zero before starting to do backpropragation because PyTorch accumulates the gradients on subsequent backward passes.
    # Because of this, when you start your training loop, ideally you should zero out the gradients so that you do the parameter update correctly.

    # Predict
    y_pred = model(data)

    # Calculate loss
    loss = F.nll_loss(y_pred, target)
    # train_losses.append(loss)
    train_loss += loss.item()

    # Backpropagation
    loss.backward()
    optimizer.step()




    # Update pbar-tqdm

    pred = y_pred.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
    correct += pred.eq(target.view_as(pred)).sum().item()
    processed += len(data)

    pbar.set_description(desc= f'Train: Loss={loss.item()} Batch_id={batch_idx} Accuracy={100*correct/processed:0.2f}')
    # train_acc.append(100*correct/processed)

  train_loss = train_loss/len(train_loader)
  train_acc = 100 * correct / processed

  # print('Training set set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(train_loss, correct, len(train_loader.dataset),train_acc))

  return train_loss, train_acc

def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    test_acc=0
    correct = 0

    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)
    test_losses.append(test_loss)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.2f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

    test_acc = (100. * correct / len(test_loader.dataset))

    return test_loss, test_acc