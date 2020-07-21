let img

let deltaX = 0
let deltaY = 0
let zoomRatio = 1

let heightAdjust = 40

function preload() {
    img = createImg(imagePath)
}

function setup() {
    createCanvas(windowWidth, windowHeight - heightAdjust)
}

function draw() {
    if (img.width > 0 ) {
        img.style('display', 'none')
        if (boundingPoly.length > 0){
            document.getElementById("remove-point").disabled = false
        } else {
            document.getElementById("remove-point").disabled = true
        }
        
        strokeWeight(1)
        background(255)
        image(img, deltaX, deltaY, img.width * zoomRatio, img.height * zoomRatio)	
        beginShape()
        boundingPoly.forEach((value, idx) => {
            noFill()
            if (idx !== 0 && idx !== boundingPoly.length - 1){
                stroke(34, 160, 34)
            } else if (idx === 0) {
                stroke(0, 0, 205)
            } else if (idx === boundingPoly.length - 1){
                stroke(220, 20, 60)
            }
            strokeWeight(2)
            circle(...calcViewPoint(value), 8)
            fill(34, 139, 34, 70)
            stroke(34, 160, 34)
            strokeWeight(2)
            vertex(...calcViewPoint(value))
        })
        endShape(CLOSE)
    } else {
        img.style('display', 'none')
        background(100)
    }
  
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight - heightAdjust)
}

function mouseDragged() {
    if (!isEdited) {
        deltaX += mouseX - pmouseX
        deltaY += mouseY - pmouseY
        adjust_deltas()
    }
}

function mouseReleased() {
    if (mouseX > 0 && mouseX < windowWidth && mouseY > 0 && mouseY < windowHeight - heightAdjust ) {
        if (isEdited) {
            if (boundingPoly.length === 10) {
                alert("The maximum count of boundings is 10.")
            } else {
                boundingPoly.push(
                    calcOriginPoint({
                        x: mouseX, 
                        y: mouseY
                    })
                )
            }
        }
    }
}

function mouseWheel(event) {
    if (event.delta < 0){
        zoomRatio *= 1.1
    } else if (event.delta > 0) {
        zoomRatio /= 1.1
    }
    adjust_deltas()
}

function isInButtonArea(pointX, pointY, width, height) {
    if (mouseX >= pointX && mouseX <= pointX + width && mouseY >= pointY && mouseY <= pointY + height) {
        return true
    } else {
        return false
    }
}

function createMyButton(pointX, pointY, width, height, backColorRGB, labelText) {
    fill(...backColorRGB)
    stroke(255)
    strokeWeight(1)
    rect(pointX, pointY, width, height, 8)
    fill(255)
    noStroke()
    text(labelText, pointX + (width - labelText.length * 6) / 2, pointY + height / 2 + 4)
}

function calcViewPoint(originPoint) {
    let viewPoint = [
        originPoint.x * img.width * zoomRatio + deltaX,
        originPoint.y * img.height * zoomRatio + deltaY
    ]
    return viewPoint
}

function calcOriginPoint(viewPoint) {
    let originPoint = {
        x: Number(((viewPoint.x - deltaX) / zoomRatio).toFixed(0)) / img.width,
        y: Number(((viewPoint.y - deltaY) / zoomRatio).toFixed(0)) / img.height

    }

    return originPoint
}

function adjust_deltas() {
    if (deltaX >= 0 || windowWidth - zoomRatio * img.width >= 0)
        deltaX = 0
    else if (windowWidth - zoomRatio * img.width < 0 && deltaX < windowWidth - zoomRatio * img.width)
        deltaX = (windowWidth - zoomRatio * img.width)
    
    if (deltaY >= 0 || (windowHeight - heightAdjust) - zoomRatio * img.height >= 0)
        deltaY = 0
    else if ((windowHeight - heightAdjust) - zoomRatio * img.height < 0 && deltaY < (windowHeight - heightAdjust) - zoomRatio * img.height)
        deltaY = ((windowHeight - heightAdjust) - zoomRatio * img.height)
}