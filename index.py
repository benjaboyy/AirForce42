
import arcade
import math
import os
import arcade.gui

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_COIN = 0.24
SPRITE_SCALING_LASER = 0.7
RANDOM_ENEMY_COUNT = 50

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 1
SPRITE_PIXEL_SIZE = 64
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1000
SCREEN_TITLE = 'AirForce 42'

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 100
RIGHT_VIEWPORT_MARGIN = 100
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

BULLET_SPEED = 7
BASIC_SCROL_SPEED = 1
START_LIVES = 3

# Speed limit player horizontal
MAX_SPEED = 6.0
# How fast we accelerate
ACCELERATION_RATE = 0.2
# How fast to slow down after we letr off the key
FRICTION = 0.1


class MyGhostFlatButton(arcade.gui.UIGhostFlatButton):
    """
    For this subclass, we create a custom init, that takes in another
    parameter, the UI text box. We use that parameter and print the contents
    of the text entry box when the ghost button is clicked.
    """

    def __init__(self, center_x, center_y, input_box):
        super().__init__(
            'GhostFlatButton',
            center_x=center_x,
            center_y=center_y,
            width=250,
            # height=20
        )
        self.input_box = input_box

    def on_click(self):
        """ Called when user lets off button """
        print(f"Click ghost flat button. {self.input_box.text}")

class InstructionView(arcade.View):
    def __init__(self):
        super().__init__()
        self.logo = 0
        # Background image will be stored in this variable
        self.background = None
        # self.ui_manager = UIManager(window)
    def on_show(self):
        # self.setup()
        self.logo = arcade.SpriteList()
        begin_logo = arcade.Sprite("img/logo.png", SPRITE_SCALING_LASER / 2)
        begin_logo.center_x = SCREEN_WIDTH / 2
        begin_logo.center_y = SCREEN_HEIGHT / 2
        self.logo.append(begin_logo)
        """ This is run once when we switch to this view """
        # Load the background image. Do this in the setup so we don't keep reloading it all the time.
        self.background = arcade.load_texture(":resources:images/backgrounds/abstract_1.jpg")

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)
    def setup(self):
        self.ui_manager.purge_ui_elements()

        y_slot = self.window.height // 4
        left_column_x = self.window.width // 4
        right_column_x = 3 * self.window.width // 4

        # left side elements
        self.ui_manager.add_ui_element(arcade.gui.UILabel(
            'UILabel',
            center_x=left_column_x,
            center_y=y_slot * 3,
        ))

        ui_input_box = arcade.gui.UIInputBox(
            center_x=left_column_x,
            center_y=y_slot * 2,
            width=300
        )
        ui_input_box.text = 'UIInputBox'
        ui_input_box.cursor_index = len(ui_input_box.text)
        self.ui_manager.add_ui_element(ui_input_box)

        button_normal = arcade.load_texture(':resources:gui_basic_assets/red_button_normal.png')
        hovered_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_hover.png')
        pressed_texture = arcade.load_texture(':resources:gui_basic_assets/red_button_press.png')
        button = arcade.gui.UIImageButton(
            center_x=left_column_x,
            center_y=y_slot * 1,
            normal_texture=button_normal,
            hover_texture=hovered_texture,
            press_texture=pressed_texture,
            text='UIImageButton'
        )
        self.ui_manager.add_ui_element(button)

        # right side elements
        button = MyFlatButton(
            'FlatButton',
            center_x=right_column_x,
            center_y=y_slot * 1,
            width=250,
            # height=20
        )
        self.ui_manager.add_ui_element(button)

        button = MyGhostFlatButton(
            center_x=right_column_x,
            center_y=y_slot * 2,
            input_box=ui_input_box
        )
        self.ui_manager.add_ui_element(button)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, SCREEN_WIDTH,
                                            0, SCREEN_HEIGHT,
                                            self.background)
        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-175,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        self.logo.draw()
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)

class Explosion(arcade.Sprite):
    """ This class creates an explosion animation """

    def __init__(self, texture_list):
        super().__init__()

        # Start at the first frame
        self.current_texture = 0
        self.textures = texture_list

    def update(self):

        # Update to the next frame of the animation. If we are at the end
        # of our frames, then delete this sprite.
        self.current_texture += 1
        if self.current_texture < len(self.textures):
            self.set_texture(self.current_texture)
        else:
            self.remove_from_sprite_lists()

class Enemy(arcade.Sprite):
    """
    This class represents the coins on our screen. It is a child class of
    the arcade library's "Sprite" class.
    """

    def follow_sprite(self, player_sprite):
        """
        This function will move the current sprite towards whatever
        other sprite is specified as a parameter.

        We use the 'min' function here to get the sprite to line up with
        the target sprite, and not jump around if the sprite is not off
        an exact multiple of SPRITE_SPEED.
        """

        if self.center_y < player_sprite.center_y:
            self.center_y += min( player_sprite.center_y - self.center_y)
        elif self.center_y > player_sprite.center_y:
            self.center_y -= min( self.center_y - player_sprite.center_y)

        if self.center_x < player_sprite.center_x:
            self.center_x += min( player_sprite.center_x - self.center_x)
        elif self.center_x > player_sprite.center_x:
            self.center_x -= min( self.center_x - player_sprite.center_x)

# class Player(arcade.Sprite):

    def update(self):
        self.center_x += self.change_x

        # Check to see if we hit the screen edge
        if self.left < 0:
            self.left = 0
            self.change_x = 0 # Zero x speed
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1
            self.change_x = 0

class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        arcade.start_render()

        # Draw player, for effect, on pause screen.
        # The previous View (GameView) was passed in
        # and saved in self.game_view.
        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        # draw an orange filter over him
        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH/2, SCREEN_HEIGHT/2+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH/2,
                         SCREEN_HEIGHT/2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # reset game
            game = GameView()
            self.window.show_view(game)

class MyGame(arcade.View):
    """ Main class. """

    def level_1(self):
        enemy = arcade.Sprite("img/en.png", SPRITE_SCALING_COIN * 4)
        enemy.name = "normal"
        enemy.center_x = 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)
        # Add top-right enemy ship
        enemy = arcade.Sprite("img/en.png", SPRITE_SCALING_COIN * 4)
        enemy.name = "normal"
        enemy.center_x = SCREEN_WIDTH - 120
        enemy.center_y = SCREEN_HEIGHT - enemy.height
        enemy.angle = 180
        self.enemy_list.append(enemy)
        self.background_map = None
        # Add top-mid enemy ship
        enemy = arcade.Sprite("img/black_plane.png", SPRITE_SCALING_COIN * 4)
        enemy.name = "fast"
        enemy.center_x = SCREEN_WIDTH/2
        enemy.center_y = SCREEN_HEIGHT - enemy.height + 250
        enemy.angle = 180
        self.enemy_list.append(enemy)

    def level_2(self):
        self.enemy_list = self.enemy_list_L2
        self.background_map = None

    def level_3(self):
        # Add top-right enemy ship
        enemy = arcade.Sprite("img/black_plane.png", SPRITE_SCALING_COIN * 4)
        enemy.center_x = SCREEN_WIDTH/2
        enemy.center_y = SCREEN_HEIGHT - enemy.height - 50
        enemy.angle = 180
        self.enemy_list.append(enemy)
        self.background_map = None

    def on_show(self):
        arcade.set_background_color(arcade.color.PALE_AQUA)

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__()

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Variables that will hold sprite lists
        self.frame_count = 0
        self.player_list = None
        self.enemy_list = None
        self.island_list = None
        self.background_map = None
        self.bullet_list = None
        self.bullet_player_list = None
        self.logo = None
        self.lives_sprite = None
        self.change_x = 0
        self.lives = START_LIVES


        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Don't show the mouse cursor
        self.window.set_mouse_visible(False)
        self.left_pressed = False
        self.right_pressed = False

        # of the explosion sprite because it
        # takes too long and would cause the game to pause.
        self.explosion_texture_list = []

        columns = 16
        count = 60
        sprite_width = 256
        sprite_height = 256
        file_name = ":resources:images/spritesheets/explosion.png"

        # Load the explosions from a sprite sheet
        self.explosion_texture_list = arcade.load_spritesheet(file_name, sprite_width, sprite_height, columns, count)

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

    def setup(self):
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        """ Set up the game and initialize the variables. """
        self.level = 1
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.island_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()
        self.bullet_player_list = arcade.SpriteList()
        self.explosions_list = arcade.SpriteList()
        self.logo = arcade.sprite

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("img/player.png", SPRITE_SCALING_PLAYER*2)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = 70
        self.player_sprite.angle = 180
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---
        # Name of map file to load
        map_name = "tile.tmx"
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'planes'
        # Name of the layer that has items for pick-up
        island_layer_name = 'islands'
        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        # -- Platforms
        self.enemy_list_L2 = arcade.tilemap.process_layer(map_object=my_map, layer_name=platforms_layer_name, scaling=TILE_SCALING, use_spatial_hash=True)

        self.island_list = arcade.tilemap.process_layer(my_map, island_layer_name, TILE_SCALING)
        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        # Create the 'physics engine'

        self.level_1()

        # Set the background color
        arcade.set_background_color(arcade.color.PALE_AQUA)

    def on_draw(self):
        """
        Render the screen.
        """
        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.island_list.draw()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.bullet_player_list.draw()
        self.player_list.draw()
        self.explosions_list.draw()
        self.logo = arcade.Sprite("img/logo.png", SPRITE_SCALING_LASER / 6)
        self.logo.center_x = 65 + self.view_left
        self.logo.center_y = 50 + self.view_bottom + (self.frame_count*BASIC_SCROL_SPEED)
        self.logo.draw()

        # Draw the ui
        # for i in range(self.lives):
        self.lives_sprite = arcade.Sprite("img/life_plane.png", SPRITE_SCALING_PLAYER * 2)
        self.lives_sprite.center_x = SCREEN_WIDTH + self.view_left - 50
        self.lives_sprite.center_y = 25 + self.view_bottom + (self.frame_count*BASIC_SCROL_SPEED)
        for i in range(self.lives):
            self.lives_sprite.draw()
            self.lives_sprite.center_x += -30
        # Render the text
        arcade.draw_text(f"Lives: {self.lives}", 120 + self.view_left, 55 + self.view_bottom + (self.frame_count*BASIC_SCROL_SPEED), arcade.color.BLACK, 16)
        arcade.draw_text(f"Score: {self.score}", 120 + self.view_left, 35 + self.view_bottom + (self.frame_count*BASIC_SCROL_SPEED), arcade.color.BLACK, 16)
        arcade.draw_text(f"Level: {self.level}", 120 + self.view_left, 15 + self.view_bottom + (self.frame_count*BASIC_SCROL_SPEED), arcade.color.BLACK, 16)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.LEFT:
            # self.change_x = -MOVEMENT_SPEED
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            # self.change_x = MOVEMENT_SPEED
            self.right_pressed = True
        if key == arcade.key.UP:
            bullet = arcade.Sprite("img/rocket.png", SPRITE_SCALING_LASER)
            bullet.center_x = self.player_sprite.center_x - 20
            bullet.center_y = self.player_sprite.center_y + 30
            bullet.change_y = BULLET_SPEED
            self.bullet_player_list.append(bullet)
            # Add the bullet to the appropriate list
            bullet = arcade.Sprite("img/rocket.png", SPRITE_SCALING_LASER)
            bullet.center_x = self.player_sprite.center_x + 20
            bullet.center_y = self.player_sprite.center_y + 30
            bullet.change_y = BULLET_SPEED
            self.bullet_player_list.append(bullet)
        elif key == arcade.key.DOWN:
            # Create a bullet
            bullet = arcade.Sprite("img/lazer_bullet.png", SPRITE_SCALING_LASER)
            bullet.center_x = self.player_sprite.center_x
            bullet.center_y = self.player_sprite.center_y + 30
            bullet.change_y = BULLET_SPEED + 3
            bullet.angle = 0

            # Add the bullet to the appropriate list
            self.bullet_player_list.append(bullet)
        if key == arcade.key.ESCAPE:
            # pass self, the current view, to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)



    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.change_x = 0

        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, modifiers):

        # Create a bullet
        bullet = arcade.Sprite("img/lazer_bullet.png", SPRITE_SCALING_LASER)
        bullet.center_x = self.player_sprite.center_x
        bullet.center_y = self.player_sprite.center_y + 30
        bullet.change_y = BULLET_SPEED + 3
        bullet.angle = 0

        # Add the bullet to the appropriate list
        self.bullet_player_list.append(bullet)

    def update(self, delta_time):
        """ Movement and game logic """
        self.frame_count += 1
        # Call update on all sprites
        self.enemy_list.update()
        self.bullet_list.update()
        self.bullet_player_list.update()
        self.explosions_list.update()
        self.view_bottom += BASIC_SCROL_SPEED - 0.5
        self.player_sprite.center_y +=  BASIC_SCROL_SPEED


        # Add some friction
        if self.change_x > FRICTION:
            self.change_x -= FRICTION
        elif self.change_x < -FRICTION:
            self.change_x += FRICTION
        else:
            self.change_x = 0

        # Apply acceleration based on the keys pressed
        if self.left_pressed and not self.right_pressed:
            self.change_x += -ACCELERATION_RATE
        elif self.right_pressed and not self.left_pressed:
            self.change_x += ACCELERATION_RATE

        if self.change_x > MAX_SPEED:
            self.change_x = MAX_SPEED
        elif self.change_x < -MAX_SPEED:
            self.change_x = -MAX_SPEED

        self.player_sprite.center_x += self.change_x

        for enemy in self.enemy_list:
            # if enemy.name == "fast":
            enemy.center_y += -0.5
        # --- Manage Scrolling ---
        # Track if we need to change the viewport

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True


        # Only scroll to integers. Otherwise we end up with pixels that
        # don't line up on the screen
        self.view_bottom = int(self.view_bottom)
        self.view_left = int(self.view_left)
        # Do the scrolling
        arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom  + self.frame_count,SCREEN_HEIGHT + self.view_bottom + self.frame_count)

        # Loop through each enemy that we have
        for enemy in self.enemy_list:
            # First, calculate the angle to the player. We could do this only when the bullet fires, but in this case we will rotate the enemy to face the player each frame, so we'll do this each frame.

            # Position the start at the enemy's current location
            start_x = enemy.center_x
            start_y = enemy.center_y
            # Get the destination location for the bullet
            for player in self.player_list:
                dest_x = player.center_x
                dest_y = player.center_y
            # Do math to calculate how to get the bullet to the destination. Calculation the angle in radians between the start points and end points. This is the angle the bullet will travel.
            x_diff = dest_x - start_x
            y_diff = dest_y - start_y
            angle = math.atan2(y_diff, x_diff)
            # Set the enemy to face the player.
            # enemy.angle = math.degrees(angle)-90

            # Shoot every 60 frames change of shooting each frame
            if self.frame_count % 60 == 0:
                bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png")
                bullet.center_x = start_x
                bullet.center_y = start_y
                # Angle the bullet sprite
                bullet.angle = math.degrees(angle)
                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the bullet travels.
                bullet.change_x = math.cos(angle) * BULLET_SPEED
                bullet.change_y = math.sin(angle) * BULLET_SPEED
                self.bullet_list.append(bullet)
        # Loop through each bullet
        for bullet in self.bullet_player_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)
            if len(hit_list) > 0:
                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)
                # Move it to the location of the coin
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y
                # Call update() because it sets which image we start on
                explosion.update()
                # Add to a list of sprites that are explosions
                self.explosions_list.append(explosion)
                # Get rid of the bullet
                bullet.remove_from_sprite_lists()
            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT + self.player_sprite.center_y:
                bullet.remove_from_sprite_lists()
            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1
        for bullet in self.bullet_list:
            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.player_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                # Make an explosion
                explosion = Explosion(self.explosion_texture_list)
                # Move it to the location of the coin
                explosion.center_x = hit_list[0].center_x
                explosion.center_y = hit_list[0].center_y
                # Call update() because it sets which image we start on
                explosion.update()
                # Add to a list of sprites that are explosions
                self.explosions_list.append(explosion)
                # Get rid of the bullet
                bullet.remove_from_sprite_lists()
            # For every coin we hit, add to the score and remove the coin
            # for player_hit in hit_list:
                # player_hit.remove_from_sprite_lists()
            if len(hit_list) > 0:
                self.lives += -1
                if self.lives == 0:
                    game_view = MyGame()
                    game_view.setup()
                    self.window.show_view(game_view)
            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT + self.player_sprite.center_y:
                bullet.remove_from_sprite_lists()

        # See if we should go to level 2
        if len(self.enemy_list) == 0 and self.level == 1:
            self.level += 1
            self.frame_count = 0
            self.view_bottom = 0
            self.player_sprite.center_y = 70
            # self.bullet_player_list = None
            # self.bullet_list = None
            self.level_2()
        # See if we should go to level 3
        elif len(self.enemy_list) == 0 and self.level == 2:
            self.level += 1
            self.frame_count = 0
            self.view_bottom = 0
            self.player_sprite.center_y = 70
            # self.bullet_player_list = None
            # self.bullet_list = None
            self.level_3()


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()