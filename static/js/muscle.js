const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f172a);

const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);

const renderer = new THREE.WebGLRenderer({
    canvas: document.getElementById("c"),
    antialias: true
});

renderer.setSize(window.innerWidth, window.innerHeight);

// LIGHTS
const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(2, 2, 5);
scene.add(light);

scene.add(new THREE.AmbientLight(0xffffff, 0.5));

// LOAD MODEL
const loader = new THREE.GLTFLoader();

let model;

loader.load(
    "/static/models/human.glb",
    function (gltf) {
        model = gltf.scene;
        model.scale.set(1.5, 1.5, 1.5);
        scene.add(model);
    }
);

camera.position.z = 3;

// CLICK DETECTION
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

window.addEventListener("click", (event) => {

    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const intersects = raycaster.intersectObject(model, true);

    if (intersects.length > 0) {
        let part = intersects[0].object.name;

        document.getElementById("selected").innerText =
            "Selected: " + part;
    }
});

// ANIMATION LOOP
function animate() {
    requestAnimationFrame(animate);

    if (model) {
        model.rotation.y += 0.002;
    }

    renderer.render(scene, camera);
}

animate();

// RESIZE
window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

function resetView() {
    if (model) model.rotation.y = 0;
}