import sublime, sublime_plugin
from sublime import Region
from collections import OrderedDict

class rtl_convertCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		cleanLines = line_split.run(self, view)

		for item in cleanLines.items():
			index = item[0]
			line = item[1]
			coord = self.view.text_point(index - 1, 0)
			line_to_replace = view.line(coord)
			view.replace(edit, line_to_replace, line)

class line_split:

	def __init__(self, view):
		self.view		= view

	def run(self, view):
		document = view.substr(sublime.Region(0, view.size()))
		lines = document.splitlines()
		dictionary = OrderedDict()
		rtl_dictionary = OrderedDict()
		properties = [
			'float',
			'clear',
			'margin',
			'padding',
			'text-align',
			'left',
			'right'
		]

		# Get entire document's content, add 
		# to a dictionary with the key being 
		# the line number
		for index, line in enumerate(lines, 1):
			dictionary[index] = line

		# Remove all commented portions of
		# the document
		dictionary = strip_comments(dictionary)

		for item in dictionary.items():
			index = item[0]
			line = item[1]

			# Ignore all irrelevant lines, including:
			# - lines that already have a direction mixin
			# - lines that are a variable
			if '.direction-mixin' in line:
				continue

			if '//rtl-ignore' in line:
				continue

			if 'content:' in line:
				continue

			if line.strip().startswith('@'):
				continue

			for property_name in properties:

				# Ignore lines that don't contain the
				# properties that we're interested in
				if property_name not in line:
					continue

				if property_name is 'float'in line:
					if 'left' or 'right' not in line:
						if '@' not in line:
							continue

				if property_name is 'clear':
					if 'left' or 'right' not in line:
						if '@' not in line:
							continue

				if property_name is 'margin':
					if 'margin:' not in line:
						if 'margin-left' or 'margin-right' not in line:
							if '@' not in line:
								continue

				if property_name is 'padding':
					if 'padding:' not in line:
						if 'padding-left' or 'padding-right' not in line:
							if '@' not in line:
								continue

				if property_name is 'text-align':
					if 'left' or 'right' not in line:
						if '@' not in line:
							continue

				rtl_dictionary[index] = amend_string(line)

		return rtl_dictionary

def strip_comments(dictionary):

	stripped_dictionary = OrderedDict()
	add_to_dic = True

	for line in dictionary.items():
		line_number = line[0]
		class_name = line[1].strip()

		if add_to_dic:

			if class_name.startswith("/*"):

				if "*/" in class_name:
					continue

				else:
					add_to_dic = False

			if class_name.startswith("//"):
				continue
				
			elif add_to_dic:
				stripped_dictionary[line_number] = line[1]

		else:

			if "*/" in class_name:
				add_to_dic = True
				continue

	return stripped_dictionary

# Split the property from it's value,
# and wrap the .direction-mixin 
# around it to prepare it for replacement
# in the document
def amend_string(line):
	tabs = "\t" * (line.count("\t") - line.lstrip().count("\t"))
	css_property = line.split(":", 1)[0].strip()
	css_value = line.split(":", 1)[1].strip().rstrip(';')
	new_line = tabs + '.direction-mixin(' + css_property + '; ' + css_value + ');'
	# print(new_line)
	return new_line

# float: left;
# float: right;
# float: none;
# text-align: center;
# text-align: left;
# text-align: right;
# clear: left;
# clear: right;
# clear: @this-is-a-value;
# clear: initial;
# clear: none;
# clear: both;
# left: 10px;
# right: 20px;
# margin-top: 20px;
# margin-left: 20px;
# margin-right: 20px;
# margin: 0 10px 20px 5px;
# padding-top: 20px;
# left: 50% !default;
# padding-left: 20px;
# padding-right: 20px;
# padding: 0 10px 20px 5px;
# .direction-mixin(left; 34903px);
# @rhtjkhjkshfjkhsdjkfjkshdfk: 45454;