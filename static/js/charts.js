document.addEventListener(
"DOMContentLoaded",
function(){

const chart =
document.getElementById(
"resultsChart"
);

if(!chart) return;

new Chart(chart,{
type:"bar",

data:{
labels:[
"Alex Johnson",
"Chris Lee",
"Maria Garcia"
],

datasets:[{
label:"Votes",

data:[
12,
8,
20
]
}]
},

options:{
responsive:true,
plugins:{
legend:{
display:true
}
}
}
});

});