# Author: Cameron Kerley
# Date: 03/1/2024

class InvalidColorElement(Exception):
    def __init__(self, element, message='Error: invalid color element'):
        """
        raised when an invalid color element is passed to the modify_color method.
        """
        self.message = message + f' {element}'
        self.element = element
        super().__init__(self.message)