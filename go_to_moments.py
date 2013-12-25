import os
import re
import functools
import sublime
import sublime_plugin

config_time = [16,19]
config_max_time = max(config_time)

#borrowed from Git Plugin by David Lynch
#https://github.com/kemayo/sublime-text-2-git/
def do_when(conditional, callback, *args, **kwargs):
  if conditional():
	  return callback(*args, **kwargs)
  sublime.set_timeout(functools.partial(do_when, conditional, callback, *args, **kwargs), 50)

class GoToMoments(sublime_plugin.WindowCommand):

	def run(self):
		# get the date and time of the log
		region = self.window.active_view().sel()[0]
		line = self.window.active_view().line(region)
		line_contents = self.window.active_view().substr(line) + '\n'
		time_to_find = line_contents[0:config_max_time]

		# find date and time in other logs
		proj_folders = self.window.folders()
		files = []

		for dir in proj_folders:
			print("[SublimeLog] : Search in directory" + dir)
			files = self.doGrep(time_to_find, dir, files)

		if len(files) == 0:
			print("[SublimeLog] " + time_to_find + " not found")
			sublime.error_message("Could not find log line with time :" + time_to_find)

		elif len(files) == 1:
			self.openFileToDefinition(files[0])

		else:
			self.files = files
			paths = []
			for path,line in files:
				paths.append(path+":"+str(line))
			self.window.show_quick_panel(paths, lambda i: self.selectFile(i))
		
	# actually do the search
	def doGrep(self, time_to_find, directory, result_files):
		out = ()
		
		for r,d,files in os.walk(directory):
			for file in files:
				fn = os.path.join(r, file)
				if (fn == self.window.active_view().file_name()):
					continue
				print("[SublimeLog] : Search in file " + file)
				outList = []
				file_desc = open(fn, "r")
				lines = file_desc.readlines()

				word = time_to_find[0:config_time[0]]
				i = 1

				for n, line in enumerate(lines):
					if word in line:
						print("[SublimeLog] : found!")
						out = (fn, n)
						outList.append(out)
						if (i == len(config_time)):
							break
						else:
							word = time_to_find[0:config_time[i]]
							i = i+1

				if (len(outList)):
					result_files.append(outList[-1])

				file_desc.close()

		return result_files

	#open the file and scroll to the definition
	def openFileToDefinition(self, response):
		file, line = response
		print("[SublimeLog] Opening file "+file+" to line "+str(line))

		window = sublime.active_window()
		new_view = window.open_file(file)

		do_when(
			lambda: not new_view.is_loading(), 
			lambda: self.cursorToPos(new_view, line)
		)

	def selectFile(self, index):
		if index > -1 and len(self.files) > index:
			self.openFileToDefinition(self.files[index])

	#move cursor to the definition too
	def cursorToPos(self, view, line):
		nav_line = line - 1
		nav_pt = view.text_point(nav_line, 0)
		fn_line = line
		pt = view.text_point(fn_line, 0)

		view.set_viewport_position(view.text_to_layout(nav_pt))

		view.sel().clear()
		view.sel().add(sublime.Region(pt))

		view.show(pt)
