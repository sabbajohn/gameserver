var canvas = document.getElementById('iframe_id');
var initializing = true;
var statusMode = 'hidden';

var animationCallbacks = [];
function animate(time) {
    animationCallbacks.forEach(callback => callback(time));
    requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
function adjustCanvasDimensions() {

    var scale = window.devicePixelRatio || 1;
    var totalWidth = window.innerWidth;
    var totalHeight = window.innerHeight - 0;
    var borders = 20;
    var totalWidthMinusBorders = totalWidth - 2*borders;
    var totalHeightMinusBorders = totalHeight - 2*borders;
    var availableAspect = totalWidthMinusBorders * 1.0 / totalHeightMinusBorders;
    var contentAspect = 16.0 / 9.0;
    var width = totalWidthMinusBorders;
    var height = totalHeightMinusBorders;
    if(availableAspect > contentAspect)
    {
        // aspectRatio of available area is wider than the aspect of the content
        // we keep the window height, and constrain the width
        width = height * contentAspect;
    }
    else
    {
        // aspectRatio of available area is narrower than the aspect of the content
        // we keep the window width, and constrain the height
        height = width / contentAspect;
    }
    canvas.width = width * scale;
    canvas.height = height * 0.56;
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    }
    animationCallbacks.push(adjustCanvasDimensions);
    adjustCanvasDimensions();
            