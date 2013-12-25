import sublime
import sublime_plugin

class TargetError(sublime_plugin.WindowCommand):

	def run(self):
		# add bookmarks
		RegionsResult = self.window.active_view().find_all(" ERROR ", sublime.IGNORECASE)
		self.window.active_view().add_regions("bookmarks", RegionsResult, "bookmarks", "bookmark", sublime.HIDDEN | sublime.PERSISTENT)

		# go to the first definition
		if (len(RegionsResult)):
			self.window.active_view().show_at_center(RegionsResult[0])	
		else:
			print("No ERROR found.")