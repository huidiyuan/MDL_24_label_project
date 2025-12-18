// =============================================================================
// CIRCLE OVERLAP EXPERIMENT - QUALTRICS VERSION (FIXED FOR MULTIPLE TRIALS)
// Stores all trial data in ONE JSON field - supports unlimited trials!
// =============================================================================

Qualtrics.SurveyEngine.addOnload(function() {
    var qThis = this;
    
    // Hide Qualtrics elements
    qThis.hideNextButton();
    qThis.questionclick = function(){} // Disable default click behavior
    
    // Get the current labels from Qualtrics Loop & Merge
    var label1 = "${lm://Field/1}";
    var label2 = "${lm://Field/2}";
    var labelType = "${lm://Field/3}";
    
    // Get trial number from Loop & Merge current loop number
    var trialNumber = parseInt("${lm://CurrentLoopNumber}");
    
    console.log("Trial " + trialNumber + " - Labels:", label1, label2, labelType);
    
    // Function to initialize the experiment
    function initExperiment() {
        
        // Generate random order indicator (0 or 1) for this trial
        var orderIndicator = Math.floor(Math.random() * 2);
        
        // Apply order based on random orderIndicator
        var leftLabel, rightLabel;
        if (orderIndicator === 1) {
            leftLabel = label2;
            rightLabel = label1;
        } else {
            leftLabel = label1;
            rightLabel = label2;
        }
        
        // Create unique container for this trial
        var containerId = 'sketch-container-' + trialNumber + '-' + Date.now();
        var container = document.createElement('div');
        container.id = containerId;
        container.style.width = '100%';
        container.style.display = 'flex';
        container.style.justifyContent = 'center';
        qThis.questionContainer.appendChild(container);
        
        // Variables to store slider values
        var sizeValue = 100;
        var overlapValue = 0;
        var sizeTouched = false;
        var overlapTouched = false;
        var startTime = Date.now();
        
        // Create p5.js sketch with instance mode
        new p5(function(p) {
            // Canvas dimensions
            const CANVAS_WIDTH = 1200;
            const CANVAS_HEIGHT = 800;
            
            // Colors
            const WHITE = [255, 255, 255];
            const BLACK = [0, 0, 0];
            const BLUE = [100, 150, 255];
            const RED = [255, 100, 100];
            const DARK_BLUE = [50, 75, 200];
            const DARK_RED = [200, 50, 50];
            const LIGHT_GRAY = [220, 220, 220];
            const DARK_GRAY = [100, 100, 100];
            const SLIDER_COLOR = [150, 150, 150];
            
            // Circle parameters
            const BASE_RADIUS = 50;
            const LEFT_CIRCLE_X = 550;
            const LEFT_CIRCLE_Y = 300;
            const CIRCLE_ALPHA = 180;
            
            // Label positions
            const LEFT_LABEL_X = 400;
            const LEFT_LABEL_Y = 120;
            const RIGHT_LABEL_X = 800;
            const RIGHT_LABEL_Y = 120;
            
            let sizeSlider, overlapSlider, nextButton;
            let showWarning = false;
            
            p.setup = function() {
                let canvas = p.createCanvas(CANVAS_WIDTH, CANVAS_HEIGHT);
                canvas.parent(containerId);
                
                sizeSlider = new Slider(300, 550, 600, 30, 10, 1000, 100, "Right Circle Size", true, 100);
                overlapSlider = new Slider(300, 650, 600, 30, 0, 100, 0, "Overlap Percentage", false, null);
                
                nextButton = {
                    x: 1050,
                    y: 720,
                    width: 120,
                    height: 50,
                    enabled: false
                };
            };
            
            p.draw = function() {
                p.background(WHITE);
                
                nextButton.enabled = sizeTouched && overlapTouched;
                if (nextButton.enabled) {
                    showWarning = false;
                }
                
                const sizeRatio = sizeValue / 100.0;
                const rightRadius = BASE_RADIUS * p.sqrt(sizeRatio);
                const rightX = calculateRightCirclePosition(overlapValue, BASE_RADIUS, rightRadius, LEFT_CIRCLE_X);
                
                // Draw circles
                drawCircleWithOutline(rightX, LEFT_CIRCLE_Y, rightRadius, RED, DARK_RED);
                drawCircleWithOutline(LEFT_CIRCLE_X, LEFT_CIRCLE_Y, BASE_RADIUS, BLUE, DARK_BLUE);
                
                // Draw labels with wrapping
                p.textSize(24);
                p.textStyle(p.NORMAL);
                p.noStroke();
                
                p.fill(DARK_BLUE);
                p.textAlign(p.CENTER);
                drawWrappedText(leftLabel, LEFT_LABEL_X, LEFT_LABEL_Y, 5);
                
                p.fill(DARK_RED);
                drawWrappedText(rightLabel, RIGHT_LABEL_X, RIGHT_LABEL_Y, 5);
                
                // Draw sliders and button
                sizeSlider.draw();
                overlapSlider.draw();
                drawButton();
                
                if (showWarning) {
                    p.textSize(22);
                    p.fill(200, 50, 50);
                    p.text("Please adjust both sliders before continuing", CANVAS_WIDTH / 2, 500);
                }
            };
            
            p.mousePressed = function() {
                sizeSlider.mousePressed();
                overlapSlider.mousePressed();
                
                if (p.mouseX >= nextButton.x && p.mouseX <= nextButton.x + nextButton.width &&
                    p.mouseY >= nextButton.y && p.mouseY <= nextButton.y + nextButton.height) {
                    
                    if (nextButton.enabled) {
                        saveAndContinue();
                    } else {
                        showWarning = true;
                    }
                }
            };
            
            p.mouseDragged = function() {
                sizeSlider.mouseDragged();
                overlapSlider.mouseDragged();
            };
            
            p.mouseReleased = function() {
                sizeSlider.mouseReleased();
                overlapSlider.mouseReleased();
            };
            
            // Slider class
            function Slider(x, y, w, h, minVal, maxVal, initVal, label, isLog, centerVal) {
                this.x = x;
                this.y = y;
                this.w = w;
                this.h = h;
                this.minVal = minVal;
                this.maxVal = maxVal;
                this.value = initVal;
                this.label = label;
                this.isLog = isLog;
                this.centerVal = centerVal;
                this.dragging = false;
                this.handleRadius = 12;
                
                this.getHandleX = function() {
                    let proportion;
                    if (this.isLog) {
                        const logMin = p.log(this.minVal) / p.log(10);
                        const logMax = p.log(this.maxVal) / p.log(10);
                        const logValue = p.log(this.value) / p.log(10);
                        proportion = (logValue - logMin) / (logMax - logMin);
                    } else {
                        proportion = (this.value - this.minVal) / (this.maxVal - this.minVal);
                    }
                    return this.x + proportion * this.w;
                };
                
                this.getCenterX = function() {
                    if (this.centerVal !== null) {
                        let proportion;
                        if (this.isLog) {
                            const logMin = p.log(this.minVal) / p.log(10);
                            const logMax = p.log(this.maxVal) / p.log(10);
                            const logCenter = p.log(this.centerVal) / p.log(10);
                            proportion = (logCenter - logMin) / (logMax - logMin);
                        } else {
                            proportion = (this.centerVal - this.minVal) / (this.maxVal - this.minVal);
                        }
                        return this.x + proportion * this.w;
                    }
                    return null;
                };
                
                this.draw = function() {
                    p.fill(LIGHT_GRAY);
                    p.stroke(DARK_GRAY);
                    p.strokeWeight(2);
                    p.rect(this.x, this.y, this.w, this.h, 5);
                    
                    const centerX = this.getCenterX();
                    if (centerX !== null) {
                        p.stroke(BLACK);
                        p.strokeWeight(3);
                        p.line(centerX, this.y, centerX, this.y + this.h);
                    }
                    
                    const handleX = this.getHandleX();
                    const filledWidth = handleX - this.x;
                    if (filledWidth > 0) {
                        p.fill(SLIDER_COLOR);
                        p.noStroke();
                        p.rect(this.x, this.y, filledWidth, this.h, 5);
                    }
                    
                    p.fill(DARK_GRAY);
                    p.noStroke();
                    p.circle(handleX, this.y + this.h / 2, this.handleRadius * 2);
                    p.fill(WHITE);
                    p.circle(handleX, this.y + this.h / 2, (this.handleRadius - 3) * 2);
                    
                    p.fill(BLACK);
                    p.textAlign(p.CENTER);
                    p.textSize(28);
                    p.noStroke();
                    p.text(this.label, this.x + this.w / 2, this.y - 30);
                    
                    if (!this.isLog) {
                        p.textSize(28);
                        p.text(p.round(this.value) + "%", this.x + this.w / 2, this.y + this.h + 25);
                    }
                    
                    if (this.isLog) {
                        p.textSize(20);
                        const labels = {10: "smaller", 100: "same", 1000: "larger"};
                        for (let val in labels) {
                            const logMin = p.log(this.minVal) / p.log(10);
                            const logMax = p.log(this.maxVal) / p.log(10);
                            const logVal = p.log(val) / p.log(10);
                            const proportion = (logVal - logMin) / (logMax - logMin);
                            const tickX = this.x + proportion * this.w;
                            p.text(labels[val], tickX, this.y - 10);
                        }
                    } else {
                        p.textSize(22);
                        p.text("0%", this.x, this.y - 12);
                        p.text("100%", this.x + this.w, this.y - 12);
                    }
                };
                
                this.mousePressed = function() {
                    const handleX = this.getHandleX();
                    const dist = p.dist(p.mouseX, p.mouseY, handleX, this.y + this.h / 2);
                    
                    if (dist <= this.handleRadius || 
                        (p.mouseX >= this.x && p.mouseX <= this.x + this.w &&
                         p.mouseY >= this.y && p.mouseY <= this.y + this.h)) {
                        this.dragging = true;
                        this.updateValue(p.mouseX);
                        
                        if (this.isLog) {
                            sizeTouched = true;
                        } else {
                            overlapTouched = true;
                        }
                    }
                };
                
                this.mouseDragged = function() {
                    if (this.dragging) {
                        this.updateValue(p.mouseX);
                    }
                };
                
                this.mouseReleased = function() {
                    this.dragging = false;
                };
                
                this.updateValue = function(mouseX) {
                    mouseX = p.constrain(mouseX, this.x, this.x + this.w);
                    const proportion = (mouseX - this.x) / this.w;
                    
                    if (this.isLog) {
                        const logMin = p.log(this.minVal) / p.log(10);
                        const logMax = p.log(this.maxVal) / p.log(10);
                        const logValue = logMin + proportion * (logMax - logMin);
                        this.value = p.pow(10, logValue);
                        sizeValue = this.value;
                    } else {
                        this.value = this.minVal + proportion * (this.maxVal - this.minVal);
                        overlapValue = this.value;
                    }
                };
            }
            
            function calculateRightCirclePosition(overlapPercent, leftRadius, rightRadius, leftX) {
                if (overlapPercent === 0) {
                    const separation = leftRadius + rightRadius;
                    return leftX + separation;
                }
                
                const smallerRadius = p.min(leftRadius, rightRadius);
                const maxOverlap = smallerRadius * 2;
                const actualOverlap = (overlapPercent / 100.0) * maxOverlap;
                const separation = leftRadius + rightRadius - actualOverlap;
                
                return leftX + separation;
            }
            
            function drawCircleWithOutline(x, y, radius, fillColor, strokeColor) {
                p.fill(fillColor[0], fillColor[1], fillColor[2], CIRCLE_ALPHA);
                p.stroke(strokeColor);
                p.strokeWeight(3);
                p.circle(x, y, radius * 2);
            }
            
            function drawButton() {
                const isHovered = p.mouseX >= nextButton.x && p.mouseX <= nextButton.x + nextButton.width &&
                                p.mouseY >= nextButton.y && p.mouseY <= nextButton.y + nextButton.height;
                
                if (nextButton.enabled) {
                    p.fill(isHovered ? SLIDER_COLOR : LIGHT_GRAY);
                } else {
                    p.fill(200, 200, 200);
                }
                
                p.stroke(DARK_GRAY);
                p.strokeWeight(2);
                p.rect(nextButton.x, nextButton.y, nextButton.width, nextButton.height, 5);
                
                p.fill(nextButton.enabled ? BLACK : [150, 150, 150]);
                p.textAlign(p.CENTER, p.CENTER);
                p.textSize(24);
                p.noStroke();
                p.text("Next", nextButton.x + nextButton.width / 2, nextButton.y + nextButton.height / 2);
            }
            
            function drawWrappedText(text, x, y, maxWordsPerLine) {
                const words = text.split(' ');
                let lines = [];
                
                for (let i = 0; i < words.length; i += maxWordsPerLine) {
                    lines.push(words.slice(i, i + maxWordsPerLine).join(' '));
                }
                
                const lineHeight = 28;
                const startY = y - ((lines.length - 1) * lineHeight) / 2;
                
                lines.forEach((line, index) => {
                    p.text(line, x, startY + index * lineHeight);
                });
            }
            
            function saveAndContinue() {
                const endTime = Date.now();
                const responseTime = (endTime - startTime) / 1000;
                
                var allTrialData = Qualtrics.SurveyEngine.getEmbeddedData('allTrialData');
                if (!allTrialData || allTrialData === '') {
                    allTrialData = [];
                } else {
                    try {
                        allTrialData = JSON.parse(allTrialData);
                    } catch (e) {
                        allTrialData = [];
                    }
                }
                
                allTrialData.push({
                    trial: trialNumber,
                    size_percent: parseFloat(sizeValue.toFixed(2)),
                    overlap_percent: parseFloat(overlapValue.toFixed(2)),
                    response_time: parseFloat(responseTime.toFixed(2)),
                    order_indicator: orderIndicator,
                    label_left: leftLabel,
                    label_right: rightLabel,
                    label_1: label1,
                    label_2: label2,
                    type: labelType
                });
                
                Qualtrics.SurveyEngine.setEmbeddedData('allTrialData', JSON.stringify(allTrialData));
                
                qThis.showNextButton();
                qThis.clickNextButton();
            }
        });
    }
    
    // Check if p5 is already loaded, if not load it
    if (typeof p5 === 'undefined') {
        var script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js';
        script.onload = function() {
            console.log("p5.js loaded");
            initExperiment();
        };
        script.onerror = function() {
            console.error("Failed to load p5.js");
        };
        document.head.appendChild(script);
    } else {
        // p5 already loaded
        initExperiment();
    }
});
