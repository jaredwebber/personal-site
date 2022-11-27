const c = document.getElementById("responsive-canvas");
const ctx = c.getContext('2d');

const loadingMessage = document.getElementById("loading-message");
const loadingBackground = document.getElementById("loading");

window.addEventListener('resize', () => {
    runBackground();
});

// animation framerate variables
var frameCount = 0;
var fps, fpsInterval, startTime, now, then, elapsed;

function startAnimating(fps) {
    fpsInterval = 1000 / fps;
    then = window.performance.now();
    startTime = then;
    animate();
}

function animate(newtime) {
    // request another frame
    requestAnimationFrame(animate);

    // calc elapsed time since last loop
    now = newtime;
    elapsed = now - then;

    // if enough time has elapsed, draw the next frame
    if (elapsed > fpsInterval) {

        // Get ready for next frame by setting then=now, but...
        // Also, adjust for fpsInterval not being multiple of 16.67
        then = now - (elapsed % fpsInterval);

        gameOfLife();
        if(loading){
            loading = false;
            loadingMessage.innerHTML = "LOADING";
            clearInterval(this.loaderInterval);
        }
        
    }
}

// Tile Constants and Variables
const RGB_COLOURS = [
    'rgb(255, 105, 97)',
    'rgb(255, 180, 128)',
    'rgb(248, 243, 141)',
    'rgb(66, 214, 164)',
    'rgb(66, 214, 164)',
    'rgb(8, 202, 209)',
    'rgb(89, 173, 246)',
    'rgb(157, 148, 255)',
    'rgb(199, 128, 232)'
]
const BW_COLOURS = [
    'rgb(255, 255, 255)',
    'rgb(255, 255, 255)',
    'rgb(0, 0, 0)',
    'rgb(0, 0, 0)',
    'rgb(255, 255, 255)',
    'rgb(255, 255, 255)',
    'rgb(255, 255, 255)',
    'rgb(255, 255, 255)',
    'rgb(255, 255, 255)',
]
const GREYSCALE_COLOURS = [
    'rgb(50, 50, 50)',
    'rgb(100, 100, 100)',
    'rgb(150, 150, 150)',
    'rgb(150, 150, 150)',
    'rgb(100, 100, 100)',
    'rgb(90, 90, 90)',
    'rgb(80, 80, 80)',
    'rgb(70, 70, 70)',
    'rgb(60, 60, 60)',
]
const BACKGROUND_COLOURS = {
    "GREYSCALE_COLOURS": 'rgb(190, 190, 190)',
    "BW_COLOURS": 'rgb(100, 100, 100)',
    "RGB_COLOURS": 'rgb(135, 206, 250)',
}
const MIN_NEIGHBOURS = 1;
const MAX_NEIGHBOURS = 4;
const REVIVE = 3;
const TILE_SIZE = 10;
const LIFE_FREQ = 0.15;
const FRAMERATE = 3;

var tileColours = GREYSCALE_COLOURS;
var rows = null;
var cols = null;
var grid = null;
var nextGrid = null;
var loaderInterval = null;
var loading = true;

class Tile {
    constructor(x, y, isAlive){
        this.size = TILE_SIZE;
        this.x = x;
        this.y = y;
        this.neighbours = 1;
        this.isAlive = isAlive;
    }
    
    drawTile(){
        ctx.beginPath();
        ctx.strokeStyle = tileColours[this.neighbours];
        ctx.rect(this.x, this.y, this.size, this.size);
        ctx.fillStyle = tileColours[this.neighbours];
        ctx.fill();
        ctx.stroke();
    }

    copyTile(){
        var newTile = new Tile(this.x, this.y, this.isAlive);
        newTile.neighbours = this.neighbours;
        return newTile;
    }
}

function toggleColours(){
    if(tileColours == BW_COLOURS){
        tileColours = GREYSCALE_COLOURS;
    }else if(tileColours == GREYSCALE_COLOURS){
        tileColours = RGB_COLOURS;
    }else{
        tileColours = BW_COLOURS;
    }
    setBackgroundColour();
}

function setBackgroundColour(){
    if(tileColours == GREYSCALE_COLOURS){
        loadingBackground.style.backgroundColor = BACKGROUND_COLOURS["GREYSCALE_COLOURS"];
    }else if(tileColours == RGB_COLOURS){
        loadingBackground.style.backgroundColor = BACKGROUND_COLOURS["RGB_COLOURS"];
        }else{
        loadingBackground.style.backgroundColor = BACKGROUND_COLOURS["BW_COLOURS"];
    }
}

function regenerateBackground(){
    runBackground();
}

function displayLoadingMessage(duration){
   if(loading) loaderInterval = setTimeout(() => {
    if(loadingMessage.innerHTML.length < 20) loadingMessage.append(".");
    displayLoadingMessage();
   }, 200);
}

function runBackground(){
    loading = true;
    displayLoadingMessage(0);
    c.width = c.clientWidth;
    c.height = c.clientHeight;
    ctx.clearRect(0, 0, c.width, c.height);
    cols = Math.floor((c.height+TILE_SIZE)/TILE_SIZE);
    rows = Math.floor((c.width+TILE_SIZE)/TILE_SIZE);
    initGrids();
    startAnimating(FRAMERATE);
}

function initGrids(){
    grid = new Array();
    nextGrid = new Array();
    for(var x = 0; x<rows; x++){
        grid[x] = new Array();
        nextGrid[x] = new Array();
        for(var y = 0; y<cols; y++){
            grid[x][y] = new Tile(x*TILE_SIZE, y*TILE_SIZE, Math.random() < LIFE_FREQ);
        }
    }
}

function drawGrid(){
    ctx.clearRect(0,0,c.width,c.height);
    for(var x = 0; x<rows; x++){
        for(var y = 0; y<cols; y++){
            grid[x][y].drawTile();
        }
    }
}

function nextGen(){
    for(var x = 0; x<rows; x++){
        for(var y = 0; y<cols; y++){
            var neighbours = 0;
            if(x-1 >= 0 && y-1 >= 0 && grid[x-1][y-1].isAlive) neighbours++;
            if(x-1>=0 && grid[x-1][y].isAlive) neighbours++;
            if(x-1>=0 && y+1 < cols && grid[x-1][y+1].isAlive) neighbours++;
            if(y-1>=0 && grid[x][y-1].isAlive) neighbours++;
            if(y+1 < cols && grid[x][y+1].isAlive) neighbours++;
            if(x+1 < rows && y-1>=0 && grid[x+1][y-1].isAlive) neighbours++;
            if(x+1<rows && grid[x+1][y].isAlive) neighbours++;
            if(x+1 < rows && y+1 < cols && grid[x+1][y+1].isAlive) neighbours++;

            nextGrid[x][y] = grid[x][y].copyTile();
            if(!grid[x][y].isAlive && neighbours == REVIVE){
                nextGrid[x][y].isAlive = true;
            }else if(grid[x][y].isAlive && (neighbours <= MIN_NEIGHBOURS || neighbours >= MAX_NEIGHBOURS)){
                nextGrid[x][y].isAlive = false;
            }
            nextGrid[x][y].neighbours = neighbours;
        }
    }
    copyGrid();
}

function copyGrid(){
    for(var x = 0; x<rows; x++){
        for(var y = 0; y<cols; y++){
            grid[x][y] = nextGrid[x][y];
        }
    }
}

function gameOfLife(){
    nextGen();
    drawGrid();
}

runBackground();
