# Command: Modern Air/Naval Operations (CMANO) Data Transformation Tool
This Python tool allows scenario designers to use table-based data to create new scenarios. Normally, designers can build a scenario manually within the game or use Lua commands to build game entities and behavior. Often, a scenario designer already has a database containing units belonging to each combatant. That data can be exported in table format, but it needs additional information and formatting before it can be inserted into the game.

The main class is CmdData, and the commandLua.py file shows a typical loading and transformation sequence.
There are several required sample files that are included here. The format and existence of these files are required.

To see further explanation, visit https://www.mbondpro.com/2018/11/python-and-lua-scripts-for-building.html

To learn more about CMANO, see here: http://www.warfaresims.com/
To learn about Lua commands in CMANO, see here: https://commandlua.github.io/

