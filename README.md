# StatTrack


      _________ __          __ ___________                     __    
     /   ______/  |______ _/  |\__    _______________    ____ |  | __
     \_____  \\   __\__  \\   __\|    |  \_  __ \__  \ _/ ___\|  |/ /
     /        \|  |  / __ \|  |  |    |   |  | \// __ \\  \___|    < 
    /_______  /|__| (____  |__|  |____|   |__|  (____  /\___  |__|_ \
            \/           \/                          \/     \/     \/


StatTrack is an interactive tool to help give you an edge with Fantasy Sports Drafts.

It currently supports NFL & NHL style drafts.


To get started do:

    % sudo apt-get install python python-bs4 python-setuptools python-pip
    % pip install jsonpickle pandas
    % git clone https://github.com/jeffdasilva/stattrack.git
    % cd stattrack
    % make run

On Windows, install msys2 + python 2.7 and then do:
    % pacman -S git make gcc dos2unix
    % python -m pip install --upgrade pip
    % python -m pip install beautifulsoup4 jsonpickle scrapy pandas lxml
