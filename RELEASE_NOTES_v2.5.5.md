# GPUStack UI v2.5.5 Release Notes

## 🎉 Major CSS Framework Overhaul

This release completely replaces Tailwind CSS with a custom CSS framework, resolving all styling issues and improving reliability.

### ✨ New Features

#### Custom CSS Framework
- **Replaced Tailwind CSS** with a comprehensive custom CSS framework
- **No build process required** - CSS is static and reliable
- **Complete utility classes** matching Tailwind's naming convention
- **CSS Custom Properties** for theming (dark/light mode support)
- **Better debugging** - direct CSS control without compilation issues

#### Fixed Asset Loading
- **Fixed all 404 errors** for JavaScript and CSS assets
- **Corrected static file paths** to use `/static/` prefix
- **Markdown rendering** now works (marked.js loads correctly)
- **Code highlighting** works (highlight.js loads correctly)
- **Theme CSS** loads properly (github-dark.min.css, github.min.css)

### 🔧 Technical Improvements

#### CSS Framework Features
- **Layout utilities**: flex, grid, positioning classes
- **Spacing system**: padding, margin, gap utilities
- **Typography**: text sizes, weights, alignment
- **Color system**: theme-aware colors with CSS variables
- **Interactive states**: hover, focus, disabled styles
- **Animations**: transitions and keyframes
- **Responsive design**: media queries for different screen sizes

#### Icon and Layout Fixes
- **Fixed icon sizing** - upload icon now properly 48px × 48px
- **Layout structure** - flexbox containers work correctly
- **Spacing consistency** - all padding and margin utilities
- **Alignment precision** - items properly centered and aligned
- **Overflow handling** - scrollable areas work correctly

### 🐛 Bug Fixes

#### CSS and Styling
- Fixed large icon issue that was affecting file upload area
- Resolved layout breaking when icon sizing was adjusted
- Fixed CSS class conflicts and specificity issues
- Corrected asset loading paths for all static files

#### Asset Loading
- Fixed 404 errors for `marked.min.js`
- Fixed 404 errors for `highlight.min.js`
- Fixed 404 errors for `github-dark.min.css`
- Fixed 404 errors for `github.min.css`
- Fixed 404 errors for `main.css`

### 🚀 Performance Improvements

#### Build Process
- **Eliminated CSS compilation** - no more build step required
- **Faster development** - instant CSS changes
- **Reduced complexity** - no Tailwind dependencies
- **Better reliability** - no build failures or missing classes

#### Static File Serving
- **Optimized asset loading** - correct paths prevent 404s
- **Improved caching** - proper cache busting with version parameters
- **Better error handling** - graceful fallbacks for missing assets

### 📁 File Structure Changes

#### Removed Files
- `tailwind.config.js` - no longer needed
- `frontend/public/styles/input.css` - replaced with main.css
- `frontend/public/styles/output.css` - replaced with main.css
- `package.json` - simplified (removed Tailwind dependencies)

#### Added Files
- `frontend/public/styles/main.css` - comprehensive custom CSS framework
- `RELEASE_NOTES_v2.5.5.md` - this file

#### Modified Files
- `frontend/public/index.html` - updated asset paths to use `/static/` prefix
- `backend/main.py` - version updated to 2.5.5
- `VERSION` - updated to 2.5.5

### 🔄 Migration Notes

#### For Developers
- **No more Tailwind build process** - CSS is now static
- **Direct CSS editing** - modify `main.css` directly
- **Utility classes preserved** - same naming as Tailwind
- **CSS variables** - use `var(--bg-primary)` etc.

#### For Users
- **No visible changes** - same interface, better reliability
- **Improved performance** - faster loading, no build delays
- **Better stability** - no more CSS compilation issues

### 🎯 Key Benefits

1. **Reliability**: No more CSS build failures or missing classes
2. **Performance**: Faster development and deployment
3. **Maintainability**: Direct CSS control without framework complexity
4. **Compatibility**: All existing functionality preserved
5. **Debugging**: Easier to troubleshoot styling issues

### 📋 Installation & Deployment

#### Quick Start
```bash
# Clone and setup
git clone <repository>
cd gpustack-ui

# Start with Docker
docker-compose up --build -d

# Access the application
open http://localhost:8001/app
```

#### Development
```bash
# No CSS build step required!
# Edit frontend/public/styles/main.css directly
# Changes are served immediately
```

### 🔮 Future Roadmap

- **Enhanced theming** - more theme options
- **Component library** - reusable CSS components
- **Performance optimization** - CSS minification for production
- **Accessibility improvements** - better focus states and contrast

---

**Version**: 2.5.5  
**Release Date**: July 5, 2025  
**Branch**: `dev-css-framework-switch`  
**Status**: ✅ Production Ready

---

*This release represents a major improvement in reliability and developer experience, eliminating the CSS compilation issues that were affecting the application's stability.* 