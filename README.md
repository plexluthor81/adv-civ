# adv-civ
A Python/Kivy implementation of Avalon Hill's classic board game Advanced Civilization

As much as I prefer playing in person, the pandemic has made that more challenging. Playing online is possible at http://civ.rol-play.com/index.php, but I have been meaning to improve my own Python programming skills, and a Civ app for mobile devices seems like it would be a good, if difficult, exercise.

Credit to https://github.com/mroughan/CivilizationMap whose board I intend to eventually ~~steal~~ leverage for my own project.

As of 2021-01-08, I'm still in the very early stages of learning how Kivy works. I got the Pong app working and installed on my phone, and went through Alexander Taylor's excellent "Crash Course" on YouTube. I think I'll approach the board game incrementally:

1. Make a simplified boardgame that does not play over the network, and is just a matter of moving takens around on a simple 2x2 grid. This will let me learn how to use images, how to snap token movements to ideal positions, and just generally get me started on the project
2. Expand the movement to the full map for Civ, including multiple nations, turn-takin, and movement rules. Movement on the full map without any rules enforcement was done around 2021-01-12.
3. Add some rules logic for Civ cards, conflict, boats, and city-building.
4. Add trade cards and trading. This step could be a stand-alone app to aid while playing on a real board. Such an app might also include a Civ card cost/credit calculator.
6. Add in calamities.
5. Flesh out the rest of the rules, including AST advancement, winning the game, and whatever else has fallen through the cracks. At this stage, hopefully I have a game that is playable at a single computer.
6. Add in networking so that the game can be played online. It might be a mistake waiting until the end to add this part, but we'll see.

Most likely I'll abandon this project. If not, I hope to make it to v0.6, where I can start playing despite the pandemic, sometime before the pandemic is over.
