# -*- coding: utf-8 -*-
"""
CommandPE Data Converter

Author: Mike Bond, 2018

"""
import os
import pandas as pd

# Provides functions to accept exported data from a wargaming or analytical database
# and convert the originating bases and units into Lua commands, which can then
# be impported into Command: Modern Air/Naval Operations (CMANO) or CommandPE (Pro Edit.)
#
# Allows scenarios to be built rapidly by compiling data in tabular form instead of 
# hand-crafting Lua commands
class CmdData:
  
   # Constructor sets up paths and buffers. Reads in initial input files.
    def __init__(self, inpath, outpath=None, outfile=None): #, skip_loads=False):
        self.buffer = []
        self.forces = []
        self.forcescopy = []
        self.forces_dbids = []
        self.bases = []
        self.aircraft = []
        self.sides = []
        self.inpath = inpath 
        self.outpath = outpath or self.inpath
        self.outfile = outfile
                
    # Perform all the necessary merges (table joins) to assign sides and game database IDs    
    def do_merges(self):
        try:
            # Map the side from the CC (country code) or 'LocationSide', for facilities
            self.aircraft = self.aircraft.merge(self.sides, how='inner', left_on='CC', right_on='DBSide')                
            self.bases = self.bases.merge(self.sides, how='inner', left_on='LocationSide', right_on='DBSide')
    
            # Add database ID to each row based on lookup table
            self.forces = self.forces.merge(self.forces_dbids, how='inner', on='UnitName')
            
            # Map the side from the CC (country code)
            self.forces = self.forces.merge(self.sides, how='inner', left_on='CC', right_on='DBSide')
           
            print("All table merges completed.\n")
        except Exception as err:
            print("*** There was a problem completing the merges.")
        
    # Clears the write buffer of Lua commands
    def clear(self):
        self.buffer = []
    
    # Load a data table from a file. 
    # Infers data contents by matching the filename, so self.bases[] should come from bases.csv
    # Arg: file name    
    def read(self, fname):
        try:
            data = pd.read_csv(os.path.join(self.inpath, fname)) # Data
            table_name = fname.split('.')[0]  # Grab data type from filename
            setattr(self,table_name,data) # Save it in the guessed attribute
            print("%s was imported successfully." % (fname))
        except Exception as err:
            print("*** There was a problem reading in a data table: %s." % (fname) )
            print("*** Make sure the filename matches the data type.")
            
        self.forcescopy = self.forces   # Copy original, to allow reverting later        
    
    # Subsets the forces dataframe according to the column and keywords
    # Args: applicable column, keyword to search e.g., ("Service", "Navy")
    # Returns length of subsetting dataframe
    def subset(self, column, keyword):
        self.forces = self.forces[self.forces[column].str.contains(keyword, case=False)]
        return len(self.forces)
    
    # Restore the copy to the main position
    # Returns the length of the restored dataframe
    def revert(self):
        self.forces = self.forcescopy
        return len(self.forces)
    
    # Adds a single unit, like base or ship, that takes a lat/longitude
    # Adds the line to the write buffer and also returns it
    # {side='LuaSideA', type='Ship', name='My Ship', dbid=383, latitude='61.490', longitude='-17.242'}
    def addUnit(self, name, unittype, lat, lng, side, dbid=1996):
        line = "ScenEdit_AddUnit({side='%s', type='%s', name=\"%s\", dbid=%u, latitude='%f', longitude='%f'})\n" % (side, unittype, name, dbid, lat, lng)
        self.buffer.append(line)
        return line

    # Adds Lua commands appropriate to assign aircraft to bases
    # Builds Lua commands from forces_dbids and aircraft dataframes and adds them to the write buffer    
    # Returns the total number of aircraft added
    def addAircraft(self):          
        self.check_clear()
                
        ac_list = self.forces_dbids.merge(self.aircraft, how='inner', left_on='UnitName', right_on='Equipment')
               
        total = 0   # Sum of all aircraft added to buffer
        for index, row in ac_list.iterrows():                        
            squadron_count = 0  # Inner loop counter to assign numbers to aircraft name
            for x in range(row['Number']):  # Quantity of aircraft of this type listed on the row
                total += 1
                squadron_count += 1
                ac_name = row['Squadron'] + " #" + str(squadron_count)  # Unique name
                line = "ScenEdit_AddUnit({side='%s', type='%s', name=\"%s\", dbid=%u, loadoutid=%u, base=\"%s\"})\n" % (row['CmdSide'], 'aircraft', ac_name, row['dbid'], row['loadoutid'], row['Base'])
                self.buffer.append(line)                                  
        print("%d aircraft added to command list." % (total))
        return total

    # Adds Lua commands appropriate to facilities like airfields and buildings
    # Builds Lua commands from self.facilities dataframe and adds them to the write buffer    
    # Returns the number of facilities added
    def addFacilities(self):
        self.check_clear()
        
        count = 0
        for index, row in self.bases.iterrows():
            self.addUnit(row['Location'], 'facility', row['Lat'], row['Lon'], row['CmdSide'], row['dbid'])
            count += 1
        print("%d facilities added to command list." % (count))
        return count
    
    # Adds Lua commands appropriate to combat forces (except aircraft)
    # Builds Lua commands from self.forces dataframe and adds them to the write buffer
    # Returns the no. of forces added
    def addForces(self):        
        self.check_clear()
        
        count = 0
        for index, row in self.forces.iterrows():
            self.addUnit(row['UnitName'], row['type'], row['Lat'], row['Lon'], row['CmdSide'], row['dbid'])
            count += 1
        print("%d forces added to command list." % (count))
        return count

    # Check if the user wants to clear the buffer and overwrite it.
    # If not, then the calling function will append new commands to the buffer
    def check_clear(self):        
      if len(self.buffer) > 0:
        response = input("Clear existing list of units from the buffer? If not, new items will be appended. (Y or N): ")
        if response.lower() == "y":
            self.clear()

    # Write the buffer to file
    # Arg: optional filename, else uses saved filename
    def write(self, fname=None):
        self.outfile = fname or self.outfile
        try:
            f = open(os.path.join(self.outpath, self.outfile), 'w')            
            f.writelines(self.buffer)
            print("\nBuffer was successfully written to %s" % (self.outfile))
        except Exception as err:
            print("Error; cannot continue. Description: " + format(err) )
        finally:
            f.close()

