let map;
    async function initMap() {
        const joinville = { lat: -26.3044, lng: -48.8461 };
        map = new google.maps.Map(document.getElementById("map"), {
            center: joinville,
            zoom: 12,
        });

        // Buscar dados do Neo4j
        fetch('/map_data')
            .then(response => response.json())
            .then(data => {
                data.forEach(item => {
                    const marker = new google.maps.Marker({
                        position: { lat: item.lat, lng: item.lng },
                        map: map,
                        title: `${item.name}\nTráfego: ${item.traffic_level}\nVelocidade: ${item.speed} km/h`
                    });
                });
            });
    }