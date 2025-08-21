# DeFi Data Snatcher - Installation Guide 🚀

## 🔧 Quick Installation

### Step 1: Download Extension
- Download or clone this repository to your computer
- Extract to a folder (e.g., `defi-data-snatcher-extension`)

### Step 2: Load in Chrome
1. Open Google Chrome
2. Navigate to `chrome://extensions/`
3. Enable **"Developer mode"** in the top right corner
4. Click **"Load unpacked"**
5. Select the extension folder
6. The extension should appear in your toolbar

### Step 3: Test the Extension
1. Visit any DeFi platform (e.g., [ButterSwap Explorer](https://explorer.butterswap.io/en))
2. Click the **DeFi Data Snatcher** icon in your toolbar
3. Click **"Preview Table Capture"**
4. Click on any transaction table
5. Review the parsed data and export

## 🎨 Icon Requirements for Chrome Web Store

**Important**: The extension includes SVG icons, but Chrome Web Store requires PNG format.

### Convert Icons to PNG:

#### Option 1: Online Converters
- [Convertio](https://convertio.co/svg-png/) - Free, easy to use
- [CloudConvert](https://cloudconvert.com/svg-to-png/) - Professional quality

#### Option 2: Command Line Tools
```bash
# Using ImageMagick
convert icons/icon16.svg icons/icon16.png
convert icons/icon32.svg icons/icon32.png
convert icons/icon48.svg icons/icon48.png
convert icons/icon128.svg icons/icon128.png

# Using Inkscape
inkscape icons/icon16.svg --export-png=icons/icon16.png
inkscape icons/icon32.svg --export-png=icons/icon32.png
inkscape icons/icon48.svg --export-png=icons/icon48.png
inkscape icons/icon128.svg --export-png=icons/icon128.png
```

### Required Icon Sizes:
- `icon16.png` - 16x16 pixels
- `icon32.png` - 32x32 pixels  
- `icon48.png` - 48x48 pixels
- `icon128.png` - 128x128 pixels

## 🚀 Chrome Web Store Submission

### Prerequisites:
1. ✅ PNG icons in all required sizes
2. ✅ Extension loads without errors
3. ✅ All functionality working properly
4. ✅ Privacy policy and terms of service

### Submission Steps:
1. Go to [Chrome Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
2. Click **"Add new item"**
3. Upload your extension package
4. Fill in store listing details
5. Submit for review

## 🧪 Testing Checklist

Before submitting to Chrome Web Store, verify:

- [ ] Extension loads without errors
- [ ] UI appears when icon is clicked
- [ ] Table detection works on various sites
- [ ] Data parsing is accurate
- [ ] CSV export functions properly
- [ ] All buttons and interactions work
- [ ] No console errors in browser

## 🔍 Troubleshooting

### Extension Won't Load:
- Check that all files are present
- Verify manifest.json syntax
- Ensure icons are in PNG format
- Check Chrome console for errors

### UI Doesn't Appear:
- Make sure you're on a supported website
- Check if content script is injected
- Verify extension permissions
- Try refreshing the page

### Parsing Issues:
- Check table structure on target website
- Verify data format matches expected patterns
- Look for console errors in browser
- Test with different websites

## 📱 Supported Platforms

- **Chrome**: Full support (primary target)
- **Edge**: Should work (Chromium-based)
- **Opera**: Should work (Chromium-based)
- **Firefox**: Not supported (different extension format)

## 🎯 Next Steps

After successful installation:

1. **Test on various DeFi platforms**
2. **Verify data accuracy**
3. **Convert icons to PNG format**
4. **Prepare Chrome Web Store listing**
5. **Submit for review**

---

**Need Help?** Check the main README.md for detailed documentation and examples.

