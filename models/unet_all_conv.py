import torch.nn as nn
import torch


# 把常用的2个卷积操作简单封装下
class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),  # 添加了BN层
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, input):
        return self.conv(input)


class Unet(nn.Module):
    def __init__(self, in_ch, out_ch, channel=16):
        super(Unet, self).__init__()
        self.conv1 = DoubleConv(in_ch, channel)
        self.pool1 = nn.Conv2d(channel, channel, 3, stride=2, padding=1)
        # self.pool1 = nn.MaxPool2d(2)
        self.conv2 = DoubleConv(channel, channel * 2)
        self.pool2 = nn.Conv2d(channel * 2, channel * 2, 3, stride=2, padding=1)
        # self.pool2 = nn.MaxPool2d(2)
        self.conv3 = DoubleConv(channel * 2, channel * 4)
        self.pool3 = nn.Conv2d(channel * 4, channel * 4, 3, stride=2, padding=1)
        # self.pool3 = nn.MaxPool2d(2)
        self.conv4 = DoubleConv(channel * 4, channel * 8)
        self.pool4 = nn.Conv2d(channel * 8, channel * 8, 3, stride=2, padding=1)
        # self.pool4 = nn.MaxPool2d(2)
        self.conv5 = DoubleConv(channel * 8, channel * 16)
        # self.pool5 = nn.MaxPool2d(2)
        # self.conv5h = DoubleConv(channel * 16, channel * 32)
        # 逆卷积，也可以使用上采样(保证k=stride,stride即上采样倍数)
        # self.up6h = nn.ConvTranspose2d(channel * 32, channel * 16, 2, stride=2)
        # self.conv6h = DoubleConv(channel * 32, channel * 16, )
        self.up6 = nn.ConvTranspose2d(channel * 16, channel * 8, 2, stride=2)
        self.conv6 = DoubleConv(channel * 16, channel * 8, )
        self.up7 = nn.ConvTranspose2d(channel * 8, channel * 4, 2, stride=2)
        self.conv7 = DoubleConv(channel * 8, channel * 4)
        self.up8 = nn.ConvTranspose2d(channel * 4, channel * 2, 2, stride=2)
        self.conv8 = DoubleConv(channel * 4, channel * 2)
        self.up9 = nn.ConvTranspose2d(channel * 2, channel, 2, stride=2)
        self.conv9 = DoubleConv(channel * 2, channel)
        self.conv10 = nn.Conv2d(channel, out_ch, 1)

    def forward(self, x):
        c1 = self.conv1(x)
        p1 = self.pool1(c1)
        c2 = self.conv2(p1)
        p2 = self.pool2(c2)
        c3 = self.conv3(p2)
        p3 = self.pool3(c3)
        c4 = self.conv4(p3)
        p4 = self.pool4(c4)
        c5 = self.conv5(p4)
        # p5 = self.pool5(c5)
        # c5h = self.conv5h(p5)
        # up_6h = self.up6h(c5h)
        # merge6h = torch.cat([up_6h, c5], dim=1)
        # c6h = self.conv6h(merge6h)
        up_6 = self.up6(c5)
        merge6 = torch.cat([up_6, c4], dim=1)
        c6 = self.conv6(merge6)
        up_7 = self.up7(c6)
        merge7 = torch.cat([up_7, c3], dim=1)
        c7 = self.conv7(merge7)
        up_8 = self.up8(c7)
        merge8 = torch.cat([up_8, c2], dim=1)
        c8 = self.conv8(merge8)
        up_9 = self.up9(c8)
        merge9 = torch.cat([up_9, c1], dim=1)
        c9 = self.conv9(merge9)
        out = self.conv10(c9)
        out = nn.Sigmoid()(out)
        return out


if __name__ == '__main__':
    model = Unet(5, 1)
    x = torch.Tensor(1, 5, 640, 640)
    y = model(x)
    print(y.shape)
