import os
import random
import json
import tkinter as tk
from PIL import Image, ImageTk, ImageEnhance, ImageDraw, ImageFilter
import pygame

class CountryFlagGame:
    def __init__(self, root, country_folder):
        self.root = root
        self.country_folder = country_folder
        self.country_list = list(set([f.replace('.png', '').split('_')[0] for f in os.listdir(country_folder) if f.endswith('.png')]))
        self.current_country = None
        self.country_options = []
        self.correct_answers = 0
        self.wrong_answers = 0
        self.timer = None
        self.lastAnswer = None

        pygame.mixer.init()
        self.correct_sound = os.path.join(country_folder, 'win.mp3')
        self.error_sound = os.path.join(country_folder, 'error_sound.mp3')

        if not self.country_list:
            print("Archivos encontrados en la carpeta:")
            for item in os.listdir(country_folder):
                print(item)
            root.destroy()
            return
        
        # Guardar la lista de países en un archivo
        self.save_country_list()

        print(f"Revisando la carpeta: {country_folder}")
        self.root.title("Juego de Países y Banderas")
        self.root.geometry("600x750")

        self.country_label = tk.Label(self.root, text="Adivina el País", font=("Helvetica", 18))
        self.country_label.pack(pady=20)

        self.canvas = tk.Canvas(self.root, width=400, height=400, bg="black")
        self.canvas.pack(pady=10)
        
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(4):
            button = tk.Button(self.buttons_frame, text="", width=20, height=2, command=lambda i=i: self.check_answer(i))
            button.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.buttons.append(button)
        
        self.progress_label = tk.Label(self.root, text=f"Aciertos: 0 / Errores: 0", font=("Helvetica", 14))
        self.progress_label.pack(pady=10)
        
        self.next_question()

    def save_country_list(self):
        country_data = ", ".join(f'"{country}"' for country in sorted(self.country_list))
        js_content = f"const paises = {{\n  countries: [{country_data}]\n}};"
        with open("paises.js", "w", encoding="utf-8") as file:
            file.write(js_content)

    def load_image(self, filepath):
        image = Image.open(filepath)
        image = image.resize((400, 400), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def load_darkened_image(self, filepath):
        image = Image.open(filepath).convert("RGBA")
        image = image.resize((400, 400), Image.LANCZOS)
        
        # Darken the entire image
        enhancer = ImageEnhance.Brightness(image)
        darkened_image = enhancer.enhance(0.2)
        
        return darkened_image

    def next_question(self):
        if not self.country_list:
            return        
        self.lastAnswer = None
        self.country_list_temp = [country for country in self.country_list if country != self.current_country]
        self.current_country = random.choice(self.country_list_temp)        
        use_shadow = random.choice([True, False])

        if use_shadow:
            shadow_image = f"{self.current_country}_sombra.png"
            image_path = os.path.join(self.country_folder, shadow_image)
            if os.path.exists(image_path):
                shadow_img = self.load_image(image_path)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor=tk.NW, image=shadow_img)
                self.canvas.image = shadow_img
                self.canvas.unbind("<Motion>")
            else:
                self.show_default_image()
        else:
            contorno_image = f"{self.current_country}_sombra.png"
            image_path = os.path.join(self.country_folder, contorno_image)
            if os.path.exists(image_path):
                self.darkened_image = self.load_darkened_image(image_path)
                self.spotlight_radius = 100
                self.canvas.bind("<Motion>", self.move_spotlight)
                self.update_spotlight(200, 200)
            else:
                self.show_default_image()
        
        self.country_options = random.sample([country for country in self.country_list if country != self.current_country], 3)
        self.country_options.append(self.current_country)
        random.shuffle(self.country_options)

        for i, option in enumerate(self.country_options):
            self.buttons[i].config(text=option.replace('.png', ''))                
        self.start_timer()

    def show_default_image(self):
        # Mostrar una imagen predeterminada si no hay sombra disponible
        image_path = os.path.join(self.country_folder, f"{self.current_country}.png")
        if os.path.exists(image_path):
            default_img = self.load_image(image_path)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=default_img)
            self.canvas.image = default_img

    def start_timer(self):
        if self.timer:
            self.root.after_cancel(self.timer)
        self.timer = self.root.after(10000, self.time_up)

    def time_up(self):
        if self.lastAnswer: return
        pygame.mixer.Sound(self.error_sound).play()
        self.wrong_answers += 1
        self.update_progress()
        if self.wrong_answers >= 3:
            response = tk.messagebox.askyesno("Juego Terminado", "Perdiste. ¿Quieres jugar de nuevo?")
            if response:
                self.correct_answers = 0
                self.wrong_answers = 0
                self.update_progress()
                self.next_question()
            else:
                self.root.destroy()
        else:
            self.show_full_country()
            self.root.after(4000, self.next_question)

    def time_up(self):
        if self.lastAnswer: return
        pygame.mixer.Sound(self.error_sound).play()
        self.wrong_answers += 1
        self.update_progress()
        if self.wrong_answers >= 3:
            pygame.mixer.Sound(self.error_sound).play()
            self.root.after(4000, self.root.destroy)
        else:
            self.show_full_country()
            self.root.after(4000, self.next_question)

    def update_spotlight(self, x, y):
        if self.lastAnswer: return
        spotlight = Image.new("L", self.darkened_image.size, 0)
        spotlight_draw = ImageDraw.Draw(spotlight)
        spotlight_draw.ellipse((x - self.spotlight_radius, y - self.spotlight_radius,
                               x + self.spotlight_radius, y + self.spotlight_radius), fill=255)
        
        spotlight = spotlight.filter(ImageFilter.GaussianBlur(10))
        
        image_with_spotlight = self.darkened_image.copy()
        image_with_spotlight.putalpha(spotlight)
        self.spotlight_img = ImageTk.PhotoImage(image_with_spotlight)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.spotlight_img)
        self.canvas.image = self.spotlight_img

    def move_spotlight(self, event):
        self.update_spotlight(event.x, event.y)

    def check_answer(self, index):
        self.show_full_country()
        self.lastAnswer = 1
        if self.country_options[index] == self.current_country:
            self.correct_answers += 1
            pygame.mixer.Sound(self.correct_sound).play()
            if self.correct_answers >= 10:
                pygame.mixer.Sound(self.correct_sound).play()
                tk.messagebox.showinfo("¡Felicidades!", "¡Has ganado el juego!")
                self.root.after(2000, self.root.destroy)
            else:
                self.root.after(2000, self.next_question)
        else:
            self.wrong_answers += 1
            pygame.mixer.Sound(self.error_sound).play()
            if self.wrong_answers >= 3:
                pygame.mixer.Sound(self.error_sound).play()
                self.root.after(2000, self.root.destroy)
            else:
                self.root.after(2000, self.next_question)
    
        self.update_progress()

    def show_full_country(self):
        full_image = f"{self.current_country}.png"
        image_path = os.path.join(self.country_folder, full_image)
        
        if os.path.exists(image_path):
            full_img = self.load_image(image_path)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=full_img)
            self.canvas.image = full_img

    def update_progress(self):
        self.progress_label.config(text=f"Aciertos: {self.correct_answers} / Errores: {self.wrong_answers}")

if __name__ == "__main__":
    root = tk.Tk()
    country_folder = os.path.dirname(os.path.abspath(__file__))  # Use the current script's directory
    print(f"Revisando la carpeta: {country_folder}")
    game = CountryFlagGame(root, country_folder)
    root.mainloop()