const fs = require('fs');
const path = require('path');
const tailwindcss = require('tailwindcss');

async function buildCSS() {
  try {
    const inputPath = path.join(__dirname, 'frontend/public/styles/input.css');
    const outputPath = path.join(__dirname, 'frontend/public/styles/output.css');
    
    // Read input CSS
    const inputCSS = fs.readFileSync(inputPath, 'utf8');
    
    // Process with Tailwind CSS v4
    const result = await tailwindcss.compile(inputCSS, {
      content: [
        'frontend/public/index.html',
        'frontend/public/**/*.js',
        'frontend/public/**/*.html'
      ]
    });
    
    // Write output CSS
    const css = await result.getStyles();
    fs.writeFileSync(outputPath, css);
    
    console.log('✅ CSS built successfully!');
    console.log(`📁 Output: ${outputPath}`);
    console.log(`📊 Size: ${(css.length / 1024).toFixed(2)} KB`);
    
  } catch (error) {
    console.error('❌ Error building CSS:', error);
    process.exit(1);
  }
}

buildCSS(); 