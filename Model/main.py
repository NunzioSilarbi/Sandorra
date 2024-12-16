import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Aventures")
fenetre.attributes("-fullscreen", True)  # Plein écran
fenetre.resizable(False, False)  # Fenêtre non redimensionnable

# Chemin du fichier JSON
dice_state_file = "./Dice.json"


# Fonction pour charger l'état des dés depuis le fichier JSON
def load_dice_state():
    if os.path.exists(dice_state_file):
        with open(dice_state_file, "r") as file:
            return json.load(file)
    else:
        # Si le fichier n'existe pas, initialiser avec tous les dés à 0 (A_Dice)
        return {"dice_1": 0, "dice_2": 0, "dice_3": 0, "dice_4": 0}


# Fonction pour sauvegarder l'état des dés dans le fichier JSON
def save_dice_state(state):
    with open(dice_state_file, "w") as file:
        json.dump(state, file)


dice_state = load_dice_state()

# Chargement des images
background_image_path = "../Vue/Castle.jpg"
profile_images = {
    "Jack": {
        "profile": "../CharacterData/Jack/Jack_PDP.jpeg",
        "stats": "../CharacterData/Jack/Jack_stats.json"
    },
    "Azazel": {
        "profile": "../CharacterData/Azazel/Azazel_PDP.jpeg",
        "stats": "../CharacterData/Azazel/Azazel_stats.json"
    },
    "Lys": {
        "profile": "../CharacterData/Lys/Lys_PDP.jpg",
        "stats": "../CharacterData/Lys/Lys_stats.json"
    },
    "Eivor": {
        "profile": "../CharacterData/Eivor/Eivor_PDP.jpeg",
        "stats": "../CharacterData/Eivor/Eivor_stats.json"
    }
}
posture_images = {
    "F": "../Vue/focus.png",
    "O": "../Vue/offensif.png",
    "D": "../Vue/defensif.png"
}

dice_image_path = "../Vue/A_Dice.png"
dice_image_alt_path = "../Vue/M_Dice.png"

# Chargement initial des images
original_background_image = Image.open(background_image_path)
profile_images_loaded = {
    name: Image.open(paths["profile"]) for name, paths in profile_images.items()
}
posture_images_loaded = {
    key: Image.open(path) for key, path in posture_images.items()
}


# Fonction pour charger les données JSON
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        return {"posture": "F"}  # Par défaut : Focus


# Fonction pour sauvegarder les données JSON
def save_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


A_Dice = Image.open(dice_image_path)
M_Dice = Image.open(dice_image_alt_path)

# Création d'un Canvas pour placer les images et les lignes
canvas = tk.Canvas(fenetre, width=800, height=600)
canvas.pack(fill="both", expand=True)

# Liste pour stocker les objets des dés
dice_objects = []


# Fonction pour changer l'état d'un dé lorsqu'il est cliqué
def toggle_dice(dice_id, dice_position):
    # Alterner l'état du dé
    dice_state[dice_id] = 1 - dice_state[dice_id]
    save_dice_state(dice_state)  # Sauvegarder le nouvel état

    # Mettre à jour l'image du dé
    update_dice_image(dice_id, dice_position)


# Fonction pour mettre à jour une image de dé
def update_dice_image(dice_id, position):
    current_state = dice_state[dice_id]
    dice_image = M_Dice if current_state == 1 else A_Dice

    # Redimensionner l'image
    resized_dice = dice_image.resize((dice_width, dice_height), Image.LANCZOS)
    dice_photo = ImageTk.PhotoImage(resized_dice)

    # Mettre à jour le Canvas
    canvas.delete(dice_id)
    canvas.create_image(position[0], position[1], image=dice_photo, anchor="center", tags=dice_id)

    # Conserver une référence pour éviter le garbage collection
    setattr(canvas, f"{dice_id}_photo", dice_photo)


# Fonction pour changer la posture d'un personnage
def toggle_posture(name, position):
    stats_file = profile_images[name]["stats"]
    stats = load_json(stats_file)

    # Alterner la posture
    posture_order = ["F", "O", "D"]  # Focus -> Offensif -> Défensif
    current_index = posture_order.index(stats["posture"])
    new_posture = posture_order[(current_index + 1) % len(posture_order)]
    stats["posture"] = new_posture

    # Sauvegarder dans le fichier JSON
    save_json(stats_file, stats)

    # Mettre à jour l'image de posture
    update_posture_image(name, new_posture, position)


# Fonction pour mettre à jour l'image de posture sur le canvas
def update_posture_image(name, posture, position):
    posture_image = posture_images_loaded[posture]
    resized_posture = posture_image.resize((posture_width, posture_height), Image.LANCZOS)
    posture_photo = ImageTk.PhotoImage(resized_posture)

    # Mettre à jour sur le canvas
    canvas.delete(f"{name}_posture")
    canvas.create_image(position[0], position[1], image=posture_photo, anchor="center", tags=f"{name}_posture")

    # Conserver la référence pour éviter le garbage collection
    setattr(canvas, f"{name}_posture_photo", posture_photo)


def adjust_hp(name, action):
    # Charger les stats depuis le fichier JSON
    stats = load_json(profile_images[name]["stats"])
    c_pv = stats.get("c_HP", 50)
    m_pv = stats.get("m_HP", 100)

    # Ajuster la valeur de PSY
    if action == "plus" and c_pv < m_pv:
        c_pv += 1  # Augmenter HP
    elif action == "minus" and c_pv > 0:
        c_pv -= 1  # Diminuer HP

    # S'assurer que c_PSY reste dans les limites
    c_pv = max(0, min(c_pv, m_pv))
    stats["c_HP"] = c_pv  # Mettre à jour dans les stats

    # Sauvegarder les stats mises à jour
    save_json(profile_images[name]["stats"], stats)

    # Actualiser le visuel
    update_bar(name, stats.get("c_PSY", 50), stats.get("m_PSY", 50), c_pv, m_pv)


# Fonction pour mettre à jour la barre de PV

def adjust_psy(name, action):
    # Charger les stats depuis le fichier JSON
    stats = load_json(profile_images[name]["stats"])
    c_psy = stats.get("c_PSY", 50)
    m_psy = stats.get("m_PSY", 100)

    # Ajuster la valeur de PSY
    if action == "plus" and c_psy < m_psy:
        c_psy += 1  # Augmenter PSY
    elif action == "minus" and c_psy > 0:
        c_psy -= 1  # Diminuer PSY

    # S'assurer que c_PSY reste dans les limites
    c_psy = max(0, min(c_psy, m_psy))
    stats["c_PSY"] = c_psy  # Mettre à jour dans les stats

    # Sauvegarder les stats mises à jour
    save_json(profile_images[name]["stats"], stats)

    # Actualiser le visuel
    update_bar(name, c_psy, m_psy, stats.get("c_HP", 50), stats.get("m_HP", 50))


# Fonction pour mettre à jour la barre de PSY
def update_bar(name, c_psy, m_psy, c_pv, m_pv):
    # Calcul de la largeur de la barre de PSY
    psy_bar_width = 300
    current_psy_width = int((c_psy / m_psy) * psy_bar_width)
    psy_bar_height = 30
    hp_bar_width = 300
    current_hp_width = int((c_pv / m_pv) * hp_bar_width)
    hp_bar_height = 30

    # Récupérer la position actuelle de la barre
    profile_position_psy = canvas.coords(f"{name}_profile")
    profile_size_psy = canvas.bbox(f"{name}_profile")[2] - canvas.bbox(f"{name}_profile")[0]
    profile_position_hp = canvas.coords(f"{name}_profile")
    profile_size_hp = canvas.bbox(f"{name}_profile")[2] - canvas.bbox(f"{name}_profile")[0]

    if profile_position_psy[0] < window_width // 2:  # Personnage à gauche
        psy_bar_position = (profile_position_psy[0] + profile_size_psy // 2 + 200, profile_position_psy[1] - 30)
    else:  # Personnage à droite
        psy_bar_position = (profile_position_psy[0] - profile_size_psy // 2 - 200, profile_position_psy[1] - 30)

    if profile_position_hp[0] < window_width // 2:
        hp_bar_position = (profile_position_hp[0] + profile_size_hp // 2 + 200, profile_position_hp[1] - 100)
    else:
        hp_bar_position = (profile_position_hp[0] - profile_size_hp // 2 - 200, profile_position_hp[1] - 100)

    # Supprimer les anciennes barres et le texte associé
    canvas.delete(f"{name}_psy")
    canvas.delete(f"{name}_psy_bg")
    canvas.delete(f"{name}_psy_text")
    canvas.delete(f"{name}_hp")
    canvas.delete(f"{name}_hp_bg")
    canvas.delete(f"{name}_hp_text")

    # Barre de fond
    canvas.create_rectangle(
        psy_bar_position[0] - psy_bar_width // 2, psy_bar_position[1] - psy_bar_height // 2,
        psy_bar_position[0] + psy_bar_width // 2, psy_bar_position[1] + psy_bar_height // 2,
        fill="gray", outline="black", tags=f"{name}_psy_bg"
    )

    # Barre actuelle
    canvas.create_rectangle(
        psy_bar_position[0] - psy_bar_width // 2, psy_bar_position[1] - psy_bar_height // 2,
        psy_bar_position[0] - psy_bar_width // 2 + current_psy_width, psy_bar_position[1] + psy_bar_height // 2,
        fill="purple", outline="black", tags=f"{name}_psy"
    )

    # Ajouter le texte des points PSY
    psy_text_position = (psy_bar_position[0], psy_bar_position[1] - psy_bar_height - 10)
    canvas.create_text(
        psy_text_position[0], psy_text_position[1]+40,
        text=f"{c_psy}/{m_psy}", font=("Arial", 14, "bold"), fill="white", tags=f"{name}_psy_text"
    )

    # Barre de fond
    canvas.create_rectangle(
        hp_bar_position[0] - hp_bar_width // 2, hp_bar_position[1] - hp_bar_height // 2,
        hp_bar_position[0] + hp_bar_width // 2, hp_bar_position[1] + hp_bar_height // 2,
        fill="gray", outline="black", tags=f"{name}_psy_bg"
    )

    # Barre actuelle
    canvas.create_rectangle(
        hp_bar_position[0] - hp_bar_width // 2, hp_bar_position[1] - hp_bar_height // 2,
        hp_bar_position[0] - hp_bar_width // 2 + current_hp_width, hp_bar_position[1] + hp_bar_height // 2,
        fill="green", outline="black", tags=f"{name}_psy"
    )

    # Ajouter le texte des points PSY
    psy_text_position = (hp_bar_position[0], hp_bar_position[1] - hp_bar_height - 10)
    canvas.create_text(
        psy_text_position[0], psy_text_position[1] + 40,
        text=f"{c_pv}/{m_pv}", font=("Arial", 14, "bold"), fill="white", tags=f"{name}_psy_text"
    )


def create_adjust_action(func, name, action):
    return lambda event: func(name, action)


# Fonction pour basculer l'état et l'image
def toggle_image(tag, stat_key, position, images, json_path):
    def handler(event):
            # Charger et modifier le fichier JSON
        data = load_json(json_path)
        current_value = data.get(stat_key, False)
        new_value = not current_value
        data[stat_key] = new_value
        save_json(json_path, data)

            # Mettre à jour l'image
        canvas.itemconfig(tag, image=images[new_value])
        setattr(canvas, f"{tag}_{stat_key}_photo", images[new_value])

    return handler

# Fonction pour redimensionner les images et remplir le fond sans bandes
def resize_images(event):
    global dice_objects
    global posture_width, posture_height
    global window_width
    # Taille de la fenêtre
    window_width = event.width
    window_height = event.height

    # --- Redimensionnement de l'image de fond ---
    original_width, original_height = original_background_image.size
    scale_ratio = max(window_width / original_width, window_height / original_height)
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)

    resized_background = original_background_image.resize((new_width, new_height), Image.LANCZOS)
    background_image = ImageTk.PhotoImage(resized_background)

    # Mise à jour de l'image de fond
    canvas.delete("background")
    canvas.create_image((window_width // 2, window_height // 2), image=background_image, anchor="center",
                        tags="background")
    canvas.background_image = background_image  # Préserve la référence pour éviter le garbage collection

    # --- Calcul des points du losange ---
    top_mid = (window_width // 2, window_height // 3)  # Milieu supérieur
    right_mid = (window_width * 2 // 3, window_height // 2)  # Milieu droit
    bottom_mid = (window_width // 2, window_height * 2 // 3)  # Milieu inférieur
    left_mid = (window_width // 3, window_height // 2)  # Milieu gauche

    # --- Dessin des lignes du losange ---
    canvas.delete("diamond")  # Supprimer l'ancien losange

    # Dessin des lignes du losange
    canvas.create_line(top_mid, right_mid, fill="black", width=4, tags="diamond")
    canvas.create_line(right_mid, bottom_mid, fill="black", width=4, tags="diamond")
    canvas.create_line(bottom_mid, left_mid, fill="black", width=4, tags="diamond")
    canvas.create_line(left_mid, top_mid, fill="black", width=4, tags="diamond")

    # --- Dessin des lignes partant des centres des côtés vers les coins du losange ---
    canvas.delete("center_lines")  # Supprimer les anciennes lignes du centre

    # Ligne partant du milieu en haut
    canvas.create_line(window_width // 2, 0, window_width // 2, window_height // 3,
                       fill="black", width=4, tags="cross")

    # Ligne partant du milieu en bas
    canvas.create_line(window_width // 2, window_height, window_width // 2, window_height * 2 // 3,
                       fill="black", width=4, tags="cross")

    # Ligne partant du milieu à gauche
    canvas.create_line(0, window_height // 2, window_width // 3, window_height // 2,
                       fill="black", width=4, tags="cross")

    # Ligne partant du milieu à droite
    canvas.create_line(window_width, window_height // 2, window_width * 2 // 3, window_height // 2,
                       fill="black", width=4, tags="cross")

    # --- Placer les dés ---
    global dice_width, dice_height
    dice_max_size = int(window_width * 0.068)  # Taille maximale de l'image de dé
    dice_ratio = min(dice_max_size / A_Dice.width, dice_max_size / A_Dice.height)
    dice_width = int(A_Dice.width * dice_ratio)
    dice_height = int(A_Dice.height * dice_ratio)

    # Calculer les positions des dés
    dice_positions = [
        (window_width // 2 - dice_width, window_height // 1.8 - dice_height),  # Haut gauche
        (window_width // 2 + dice_width, window_height // 1.8 - dice_height),  # Haut droit
        (window_width // 2 + dice_width, window_height * 1.8 // 4 + dice_height),  # Bas droit
        (window_width // 2 - dice_width, window_height * 1.8 // 4 + dice_height)  # Bas gauche
    ]

    # Mettre à jour chaque dé
    for i, position in enumerate(dice_positions):
        dice_id = f"dice_{i + 1}"
        canvas.tag_bind(dice_id, "<Button-1>", lambda event, id=dice_id, pos=position: toggle_dice(id, pos))
        update_dice_image(dice_id, position)

    else:
        print("Erreur : dimensions de l'image A_Dice invalides")

        # --- Gestion des barres de PSY ---
        profile_max_size = int(window_width * 0.22)
        posture_max_size = int(window_width * 0.068)

        profile_positions = [
            (profile_max_size // 2, profile_max_size // 2),
            (window_width - profile_max_size // 2, profile_max_size // 2),
            (profile_max_size // 2, window_height - profile_max_size // 2),
            (window_width - profile_max_size // 2, window_height - profile_max_size // 2),
        ]

        # Itérer sur les personnages
        for i, (name, paths) in enumerate(profile_images.items()):
            profile_image = profile_images_loaded[name]
            resized_profile = profile_image.resize((profile_max_size, profile_max_size), Image.LANCZOS)
            profile_photo = ImageTk.PhotoImage(resized_profile)

            # Ajouter les images de profil
            position = profile_positions[i]
            canvas.create_image(position[0], position[1], image=profile_photo, anchor="center", tags=f"{name}_profile")
            setattr(canvas, f"{name}_profile_photo", profile_photo)

            # Charger les stats
            stats = load_json(paths["stats"])
            m_psy = stats.get("m_PSY", 100)
            c_psy = stats.get("c_PSY", 50)
            m_pv = stats.get("m_HP", 100)
            c_pv = stats.get("c_HP", 50)
            posture = stats.get("posture", "F")
            avantage = stats.get("avantage", False)
            desavantage = stats.get("desavantage", False)

            # Charger les images A0, A1, D0, D1
            a_images = {
                False: ImageTk.PhotoImage(Image.open("../Vue/A0.png").resize((100, 100), Image.LANCZOS)),
                True: ImageTk.PhotoImage(Image.open("../Vue/A1.png").resize((100, 100), Image.LANCZOS))
            }
            d_images = {
                False: ImageTk.PhotoImage(Image.open("../Vue/D0.png").resize((100, 100), Image.LANCZOS)),
                True: ImageTk.PhotoImage(Image.open("../Vue/D1.png").resize((100, 100), Image.LANCZOS))
            }

            setattr(canvas, f"{name}_a_images", a_images)
            setattr(canvas, f"{name}_d_images", d_images)

            # Ajouter l'image de posture
            posture_image = posture_images_loaded[posture]
            posture_width = posture_max_size
            posture_height = posture_max_size

            # Calculer la position de l'image de posture
            if position[0] < fenetre.winfo_width() // 2:  # Si le personnage est sur la gauche
                posture_position = (position[0] + profile_max_size // 2 + 60, position[1] + 100)  # Position à droite
            else:  # Si le personnage est sur la droite
                posture_position = (
                    position[0] - profile_max_size // 2 + 40 - posture_width, position[1] + 100)  # Position à gauche

            # Mettre à jour l'image de posture
            update_posture_image(name, posture, posture_position)

            # Lier un clic pour changer la posture
            canvas.tag_bind(f"{name}_posture", "<Button-1>",
                            lambda event, n=name, pos=posture_position: toggle_posture(n, pos))

            # Calcul de la barre de PSY
            psy_bar_width = 300
            current_psy_width = int((c_psy / m_psy) * psy_bar_width)
            psy_bar_height = 30
            profile_position = profile_positions[i]

            if profile_position[0] < window_width // 2:
                psy_bar_position = (profile_position[0] + profile_max_size // 2 + 200, profile_position[1] - 30)
            else:
                psy_bar_position = (profile_position[0] - profile_max_size // 2 - 200, profile_position[1] - 30)

            # Barre de fond
            canvas.create_rectangle(
                psy_bar_position[0] - psy_bar_width // 2, psy_bar_position[1] - psy_bar_height // 2,
                psy_bar_position[0] + psy_bar_width // 2, psy_bar_position[1] + psy_bar_height // 2,
                fill="gray", outline="black", tags=f"{name}_psy_bg"
            )

            # Barre actuelle
            canvas.create_rectangle(
                psy_bar_position[0] - psy_bar_width // 2, psy_bar_position[1] - psy_bar_height // 2,
                psy_bar_position[0] - psy_bar_width // 2 + current_psy_width, psy_bar_position[1] + psy_bar_height // 2,
                fill="purple", outline="black", tags=f"{name}_psy"
            )

            # Ajouter le texte des points PSY
            psy_text_position = (psy_bar_position[0], psy_bar_position[1] - psy_bar_height - 10)
            canvas.create_text(
                psy_text_position[0], psy_text_position[1] + 40,
                text=f"{c_psy}/{m_psy}", font=("Arial", 14, "bold"), fill="white", tags=f"{name}_psy_text"
            )

            # Bouton moins
            minus_image = Image.open("../Vue/Minus.png").resize((psy_bar_height, psy_bar_height), Image.LANCZOS)
            minus_photo = ImageTk.PhotoImage(minus_image)
            minus_position = (psy_bar_position[0] - psy_bar_width // 2 - psy_bar_height, psy_bar_position[1])
            canvas.create_image(minus_position, image=minus_photo, anchor="center", tags=f"{name}_minus_psy")
            setattr(canvas, f"{name}_minus_photo", minus_photo)

            canvas.tag_bind(
                f"{name}_minus_psy", "<Button-1>",
                create_adjust_action(adjust_psy, name, "minus")
            )

            # Bouton plus
            plus_image = Image.open("../Vue/Plus.png").resize((psy_bar_height, psy_bar_height), Image.LANCZOS)
            plus_photo = ImageTk.PhotoImage(plus_image)
            plus_position = (psy_bar_position[0] + psy_bar_width // 2 + psy_bar_height, psy_bar_position[1])
            canvas.create_image(plus_position, image=plus_photo, anchor="center", tags=f"{name}_plus_psy")
            setattr(canvas, f"{name}_plus_photo", plus_photo)

            canvas.tag_bind(
                f"{name}_plus_psy", "<Button-1>",
                create_adjust_action(adjust_psy, name, "plus")
            )

            # Calcul de la barre de PV
            hp_bar_width = 300
            current_hp_width = int((c_pv / m_pv) * hp_bar_width)
            hp_bar_height = 30
            profile_position = profile_positions[i]

            if profile_position[0] < window_width // 2:
                hp_bar_position = (profile_position[0] + profile_max_size // 2 + 200, profile_position[1] - 100)
            else:
                hp_bar_position = (profile_position[0] - profile_max_size // 2 - 200, profile_position[1] - 100)

            # Barre de fond
            canvas.create_rectangle(
                hp_bar_position[0] - hp_bar_width // 2, hp_bar_position[1] - hp_bar_height // 2,
                hp_bar_position[0] + hp_bar_width // 2, hp_bar_position[1] + hp_bar_height // 2,
                fill="gray", outline="black", tags=f"{name}_hp_bg"
            )

            # Barre actuelle
            canvas.create_rectangle(
                hp_bar_position[0] - hp_bar_width // 2, hp_bar_position[1] - hp_bar_height // 2,
                hp_bar_position[0] - hp_bar_width // 2 + current_hp_width, hp_bar_position[1] + hp_bar_height // 2,
                fill="green", outline="black", tags=f"{name}_hp"
            )

            # Ajouter le texte des points PSY
            hp_text_position = (hp_bar_position[0], hp_bar_position[1] - hp_bar_height - 10)
            canvas.create_text(
                hp_text_position[0], hp_text_position[1] + 40,
                text=f"{c_pv}/{m_pv}", font=("Arial", 14, "bold"), fill="white", tags=f"{name}_hp_text"
            )

            # Bouton moins
            minus_image_hp = Image.open("../Vue/Minus.png").resize((hp_bar_height, hp_bar_height), Image.LANCZOS)
            minus_photo_hp = ImageTk.PhotoImage(minus_image_hp)
            minus_position = (hp_bar_position[0] - hp_bar_width // 2 - hp_bar_height, hp_bar_position[1])
            canvas.create_image(minus_position, image=minus_photo_hp, anchor="center", tags=f"{name}_minus_hp")
            setattr(canvas, f"{name}_minus_photo_hp", minus_photo_hp)

            canvas.tag_bind(
                f"{name}_minus_hp", "<Button-1>",
                create_adjust_action(adjust_hp, name, "minus")
            )

            # Bouton plus
            plus_image_hp = Image.open("../Vue/Plus.png").resize((hp_bar_height, hp_bar_height), Image.LANCZOS)
            plus_photo_hp = ImageTk.PhotoImage(plus_image_hp)
            plus_position = (hp_bar_position[0] + hp_bar_width // 2 + hp_bar_height, hp_bar_position[1])
            canvas.create_image(plus_position, image=plus_photo_hp, anchor="center", tags=f"{name}_plus_hp")
            setattr(canvas, f"{name}_plus_photo_hp", plus_photo_hp)

            canvas.tag_bind(
                f"{name}_plus_hp", "<Button-1>",
                create_adjust_action(adjust_hp, name, "plus")
            )

            # Déterminer les positions des images
            if position[1] < fenetre.winfo_height() // 2:  # Personnage en haut
                a0_position = (position[0] - 50, position[1] + profile_max_size // 2 + 60)
                d0_position = (position[0] + 50, position[1] + profile_max_size // 2 + 60)
            else:  # Personnage en bas
                a0_position = (position[0] - 50, position[1] - profile_max_size // 2 - 60)
                d0_position = (position[0] + 50, position[1] - profile_max_size // 2 - 60)

            # Ajouter les images A et D
            canvas.create_image(
                a0_position[0], a0_position[1],
                image=a_images[avantage],
                anchor="center",
                tags=f"{name}_a"
            )
            canvas.create_image(
                d0_position[0], d0_position[1],
                image=d_images[desavantage],
                anchor="center",
                tags=f"{name}_d"
            )

            # Associer les clics pour A et D
            canvas.tag_bind(
                f"{name}_a", "<Button-1>",
                toggle_image(f"{name}_a", "avantage", a0_position, a_images, paths["stats"])
            )
            canvas.tag_bind(
                f"{name}_d", "<Button-1>",
                toggle_image(f"{name}_d", "desavantage", d0_position, d_images, paths["stats"])
            )

            print(f"Position A0: {a0_position}, D0: {d0_position}")

# Lier l'événement de redimensionnement à la fonction
fenetre.bind("<Configure>", resize_images)

# Boucle principale de l'interface
fenetre.mainloop()
