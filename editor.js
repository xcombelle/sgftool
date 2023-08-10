"use strict";
let b_first=false;
let first = undefined;
let second = undefined;

let input= [];
let selection= [];



function refreshBackground(selection) {
    console.log("state",state);
    for (var x=0 ; x !== 21; x++) {
        for (var y=0; y !== 21; y++) {
            var el=document.getElementById(x.toString()+"_"+y.toString());
            if (state == "firstChosen") {
                //console.log("aqui",[y,x],first); // TODO: investaigate wht reverse
                if (x== first[0] && y == first[1]) {
                    console.log("sdfjhkjsdfjhkdk");
                    el.style.backgroundColor = "red";
                } else {
                    el.style.backgroundColor = "white";
                }
            } else {
             
            
            
                if (some_selected(selection)) {
                    if(selection[x][y]) {
                        el.style.backgroundColor ="green";
                    }
                    else {
                        el.style.backgroundColor ="white";
                    }
                }
            }
        }
    }
}

function some_selected(selection) {
    for (var x=0 ; x !==21 ; x++) {
        for (var y=0;y !== 21; y++) {
            if(selection[x][y]) {
                return true;
            }
        }
    }
    return false;
} 

function create_json(input, selection) {
    var result = []
    for (var x=0 ; x !==21;  x++) {
        
        for (var y=0; y !=21; y++) {
            if(some_selected(selection)) {
                if( selection[x][y] ){
                    result.push([x,y,input[x][y]]);
                }
            } else {
                result.push([x,y,input[x][y]]);
                
            }
        }
    }
    return result;
} 
let state = "norect"; 
function constructor(square,input,selection,xx,yy) {

    return function(event) {
        const select_mode = document.getElementById("select_mode").checked;
        const rectangle = document.getElementById("rectangle").checked;

        console.log(select_mode, rectangle);    
        if (!select_mode) {
            change_square(square,input,xx,yy);
        } else {
            if (rectangle) {
                
                if (state==="norect") {
                    state = "firstChosen";
                    first=[xx,yy];
                    selection = [];
                    for(var x =0; x!==21; x++) {
                        input.push([]);
                        selection.push([]);
                    }
                } else {
                    state = "secondChosen";
                    second=[xx,yy];
                    let max_y = Math.max(first[1],second[1]);
                    let min_y = Math.min(first[1],second[1]);
                    let max_x = Math.max(first[0],second[0]);
                    let min_x = Math.min(first[0],second[0]);
                    for (var x=0 ; x !==21; x++) {
                        for (var y=0; y !== 21; y++) {
                            selection[x][y] = false;
                        }
                    }
                    for (var x=min_x; x <= max_x; x++) {
                        for (var y=min_y; y <= max_y; y++) {
                            selection[x][y] = true;
                        }
                    }
                    state="norect"
                }
            } else {
                selection[xx][yy] = !selection[xx][yy];
            }
            
        }
          
        refreshBackground(selection);
        document.getElementsByTagName("pre")[0].textContent= "'"+JSON.stringify({
            point_list:create_json(input,selection),
            size: 21,
            symetries: true,
            color_exact: false,
        })+"'";
    
    }

};
for(var x =0; x!==21; x++) {
    input.push([]);
    selection.push([])
    for (var y = 0; y!== 21; y++) {
        input[x][y] = (x===0 || x===20 || y === 0|| y===20) ? " Z ": " - ";
        selection[x][y] = false;
        var square = document.getElementById(x.toString()+'_'+y.toString());
        refresh(input,x,y);
        square.addEventListener('click',constructor(square, input, selection,x, y));
    }
}


function change_square(square, input, x, y) {
    var r;
    switch( input[x][y]) {
        case " - ": 
            r = ' X '; 
            break;
        case " X ":
            r= ' O ';
            break;
        case  " O ":
            r = " - ";
            break;
        case " Z " :
            r=" Z ";
            break;
    }
    input[x][y] = r;
    refresh(input,x,y);
}

function refresh(input, x, y) {
    let square = document.getElementById( x.toString()+"_"+y.toString());
    square.innerHTML = input[x][y];
    
}
