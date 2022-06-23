class Button():
    def __init__(self, x, y, image, text_input, font, base_color, hovering_color) -> None:
        self.image = image
        self.x, self.y = x, y
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def draw(self, win) -> None:
        # win.blit(self.image, (self.rect.x, self.rect.y))
        win.blit(self.text, (self.rect.x, self.rect.y))

    # checks for movement within the button's area
    def check_for_input(self, pos) -> bool:
        print(self.text_input + "," + str(pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom)))
        return (pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range(self.rect.top, self.rect.bottom))

    # changes images within a button
    def change_image(self, image) -> None:
        self.image = image
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x, self.y))

    # changes text within a button
    def change_text(self, text_input) -> None:
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    # changes color of a button to hovering_color
    def change_color(self, pos) -> None:
        if self.check_for_input(pos):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)