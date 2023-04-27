var csvContent = "data:text/csv;charset=utf-8," + words.map(e=>e["word"]).join(",\n");

var encodedUri = encodeURI(csvContent);
var link = document.createElement("a");
link.setAttribute("href", encodedUri);
link.setAttribute("download", "my_data.csv");
document.body.appendChild(link); // Required for FF

link.click(); // This will download the data file named "my_data.csv".



var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(words));
var dlAnchorElem = document.getElementById('downloadAnchorElem');
dlAnchorElem.setAttribute("href",     dataStr     );
dlAnchorElem.setAttribute("download", "scene.json");
dlAnchorElem.click();





var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(words));
var downloadAnchorNode = document.createElement('a');
downloadAnchorNode.setAttribute("href",     dataStr);
downloadAnchorNode.setAttribute("download","words.json");
document.body.appendChild(downloadAnchorNode); // required for firefox
downloadAnchorNode.click();
downloadAnchorNode.remove();