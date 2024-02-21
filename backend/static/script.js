function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
}

function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft = "0";
}

function displaySection(sectionId) {
    // Hide all sections
    var sections = document.getElementsByTagName('section');
    for (var i = 0; i < sections.length; i++) {
        sections[i].classList.add('hidden');
    }
    // Show the selected section
    document.getElementById(sectionId).classList.remove('hidden');
}
