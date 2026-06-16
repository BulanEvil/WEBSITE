# Contact QR Assets

This folder contains only cropped QR images used by the published site.

Published files:

- `annie-whatsapp-cropped.jpg`
- `annie-wechat-cropped.jpg`
- `joe-whatsapp-cropped.jpg`
- `joe-wechat-cropped.png`

Original source files are kept in the workspace-level `contact/` folder.

When replacing a QR code:

1. Put the original image in the workspace-level `contact/` folder.
2. Crop excess white border while preserving enough white quiet zone for scanning.
3. Save the published file here using the same filename.
4. Verify `contact.html` and the header popover still load correctly.
