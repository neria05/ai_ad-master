const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');


function drawRoundedRectangle(ctx, x, y, width, height, radius, fill, border) {
  ctx.fillStyle = fill;
  ctx.strokeStyle = border.color;
  ctx.lineWidth = border.width;
  

  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.arcTo(x + width, y, x + width, y + radius, radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.arcTo(x + width, y + height, x + width - radius, y + height, radius);
  ctx.lineTo(x + radius, y + height);
  ctx.arcTo(x, y + height, x, y + height - radius, radius);
  ctx.lineTo(x, y + radius);
  ctx.arcTo(x, y, x + radius, y, radius);
  ctx.closePath();

  ctx.fill();
  ctx.stroke();
}


function drawRightToLeftText(ctx, text, x, y, font, color) {
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';

  // Reverse the text to handle right-to-left rendering
  const reversedText = text.split('').reverse().join('');

  let currentPosition = x;

  // Measure and draw each character from right to left
  for (let char of reversedText) {
    const charWidth = ctx.measureText(char).width;
    currentPosition -= charWidth;
    ctx.fillText(char, currentPosition, y);
  }
}

async function generateImage(title,subtitle, CTA,logoPath,backgroundImage,color1,color2) {
  const canvasWidth = 600;
  const canvasHeight = 800;
  const canvas = createCanvas(canvasWidth, canvasHeight);
  const ctx = canvas.getContext('2d');

  
  // if the main color is too light, then use a darker color
  if (color1.match(/^#[0-9a-f]{6}$/i)) {
    const color1RGB = color1.match(/[A-Za-z0-9]{2}/g).map((v) => parseInt(v, 16));
    const brightness = (color1RGB[0] * 299 + color1RGB[1] * 587 + color1RGB[2] * 114) / 1000;
    if (brightness > 125) {
      color1 = '#1f467a';
    }
  }

  // if the secondary color is too light, then use a darker color
  if (color2.match(/^#[0-9a-f]{6}$/i)) {
    const color2RGB = color2.match(/[A-Za-z0-9]{2}/g).map((v) => parseInt(v, 16));
    const brightness = (color2RGB[0] * 299 + color2RGB[1] * 587 + color2RGB[2] * 114) / 1000;
    if (brightness > 125) {
      color2 = '#d43f49';
    }
  }

  // Fill the canvas with white background
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvasWidth, canvasHeight);

  ctx.fillStyle = color1;
  ctx.roundRect(-100, 0, 480, 200, 60);
  ctx.fill();

  ctx.fillStyle = color1;
  ctx.roundRect(400, 600, 350, 350,40);
  ctx.fill();

  

  

  const roundedRectConfig = {
    x: 300,
    y: 50,
    width: 400,
    height: 115,
    radius: 70,
    fill: 'white', // White fill color
    border: {
      color: color1, // Purple border color
      width:3, // Border width
    },
  };
  drawRoundedRectangle(ctx, roundedRectConfig.x, roundedRectConfig.y, roundedRectConfig.width, roundedRectConfig.height, roundedRectConfig.radius, roundedRectConfig.fill, roundedRectConfig.border);

  const roundedRectConfig2 = {
    x: 190,
    y: 680,
    width: 320,
    height: 65,
    radius: 20,
    fill: 'white', // White fill color
    border: {
      color: color1, // Purple border color
      width:3, // Border width
    },
  };
  drawRoundedRectangle(ctx, roundedRectConfig2.x, roundedRectConfig2.y, roundedRectConfig2.width, roundedRectConfig2.height, roundedRectConfig2.radius, roundedRectConfig2.fill, roundedRectConfig2.border);

  // Load the logo image
  const logo = await loadImage(logoPath);

  // Draw the logo image
  ctx.drawImage(logo, 400, 38, 140, 130);



  drawRightToLeftText(ctx, title, 450, 310, '36px Arial', color1);

  
  drawRightToLeftText(ctx, subtitle, 350, 350, '28px Arial', color2);

  ctx.fillStyle = color1;
  ctx.fillRect(0, 540, 45, 40);

  const circleConfig = {
    x: 130,
    y: 550,
    radius: 100,
    border: {
      color: color1, // Purple border color
      width: 10, // Border width
    },
  };
  
  // Draw the circular border
  ctx.fillStyle = 'transparent'; // Transparent fill color for the border
  ctx.strokeStyle = circleConfig.border.color;
  ctx.lineWidth = circleConfig.border.width;
  ctx.beginPath();
  ctx.arc(circleConfig.x, circleConfig.y, circleConfig.radius, 0, 2 * Math.PI);
  ctx.closePath();
  ctx.stroke();

  // Load and draw the circular image
  const circularImage = await loadImage(backgroundImage);
  ctx.save();
  ctx.beginPath();
  ctx.arc(circleConfig.x, circleConfig.y, circleConfig.radius, 0, 2 * Math.PI);
  ctx.closePath();
  ctx.clip();
  ctx.drawImage(circularImage, circleConfig.x - circleConfig.radius, circleConfig.y - circleConfig.radius, circleConfig.radius * 2, circleConfig.radius * 2);
  ctx.restore();

  const roundedRectConfig3 = {
    x: 190,
    y: 680,
    width: 80,
    height: 65,
    radius: 20,
    fill: color1, // White fill color
    border: {
      color: color1, // Purple border color
      width:3, // Border width
    },
  };
  drawRoundedRectangle(ctx, roundedRectConfig3.x, roundedRectConfig3.y, roundedRectConfig3.width, roundedRectConfig3.height, roundedRectConfig3.radius, roundedRectConfig3.fill, roundedRectConfig3.border);
 
  drawRightToLeftText(ctx, CTA, 450, 710, '22px Arial', color2);

  // Save the canvas as a PNG file
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync('output.png', buffer);

  console.log('Canvas saved as output.png');
}

try {
  const args = process.argv.slice(2);
  const [title, subtitle, CTA,logoImage,bgImage,color1,color2] = args;

  // const logoImage = 'logos/logo_no_bg.png';
  // const backgroundImage = 'bg/bg.jpeg';
  console.log(title, subtitle, CTA,color1,color2)
  logoPath='logos/logo_no_bg.png';
  

  generateImage(title, subtitle,CTA,logoPath,bgImage,color1,color2);
} catch (error) {
  console.error('Image generation error:', error);
  process.exit(1); // Exit the Node.js script with a non-zero status code
}


module.exports = generateImage;