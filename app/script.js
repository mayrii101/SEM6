const zones = [
  { name: "Main Stage", x: 5, y: 10, w: 40, h: 30 },
  { name: "Food Court", x: 55, y: 10, w: 30, h: 20 },
  { name: "Dance Tent", x: 10, y: 50, w: 35, h: 25 }
];

const map = document.getElementById("map");

function getColor(crowd) {
  if (crowd > 70) return "red";
  if (crowd > 40) return "orange";
  return "green";
}

function renderMap() {
  map.innerHTML = "";

  zones.forEach(zone => {
    const crowd = Math.floor(Math.random() * 100);

    const div = document.createElement("div");

    div.className = `zone ${getColor(crowd)}`;

    div.style.left = zone.x + "%";
    div.style.top = zone.y + "%";
    div.style.width = zone.w + "%";
    div.style.height = zone.h + "%";

    div.innerHTML = `${zone.name}<br>${crowd}%`;

    map.appendChild(div);
  });
}

renderMap();

setInterval(renderMap, 2000);