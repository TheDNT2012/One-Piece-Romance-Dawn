#!/usr/bin/env python3
"""One Piece: Romance Dawn - versión jugable en consola.

Ejecuta:
    python3 juego.py
"""

from dataclasses import dataclass
import random
import sys
import time


# ---------- Utilidades de UI ----------


def pausa(segundos: float = 0.8) -> None:
    time.sleep(segundos)


def titulo(texto: str) -> None:
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def dialogo(personaje: str, texto: str) -> None:
    print(f"{personaje}: {texto}")


def narrador(texto: str) -> None:
    print(f"\n{texto}")


def elegir_opcion(prompt: str, opciones: list[str]) -> int:
    print(f"\n{prompt}")
    for i, opcion in enumerate(opciones, start=1):
        print(f"  {i}. {opcion}")

    while True:
        valor = input("> ").strip().lower()
        if valor.isdigit():
            idx = int(valor) - 1
            if 0 <= idx < len(opciones):
                return idx

        # Atajos por nombre
        for i, opcion in enumerate(opciones):
            clave = opcion.split("—")[0].strip().lower()
            if valor == clave or valor in opcion.lower():
                return i

        print("Opción no válida. Elige un número o escribe parte de la opción.")


# ---------- Entidades ----------


@dataclass
class Personaje:
    nombre: str
    hp_max: int
    hp: int
    atk: int
    defensa: int

    def vivo(self) -> bool:
        return self.hp > 0

    def recibir_danio(self, danio: int) -> int:
        real = max(1, danio - self.defensa)
        self.hp = max(0, self.hp - real)
        return real


@dataclass
class Jugador(Personaje):
    nivel: int = 1
    xp: int = 0
    xp_objetivo: int = 10
    stamina: int = 20

    def estado(self) -> str:
        return (
            f"LV {self.nivel} | HP {self.hp}/{self.hp_max} | "
            f"ATK {self.atk} | DEF {self.defensa} | XP {self.xp}/{self.xp_objetivo}"
        )

    def ganar_xp(self, cantidad: int) -> None:
        self.xp += cantidad
        print(f"\n+{cantidad} XP")
        while self.xp >= self.xp_objetivo:
            self.xp -= self.xp_objetivo
            self.subir_nivel()

    def subir_nivel(self) -> None:
        self.nivel += 1
        self.xp_objetivo += 10
        self.hp_max += 15
        self.hp = self.hp_max
        self.atk += 3
        self.defensa += 2
        self.stamina = min(30, self.stamina + 5)
        titulo("🎉 ¡SUBIDA DE NIVEL!")
        print(self.estado())


# ---------- Combate ----------


def dano_ataque_luffy(jugador: Jugador, ataque: str) -> tuple[int, int]:
    """Retorna (daño base, costo_stamina)."""
    if ataque == "Pistola Goma Goma":
        return jugador.atk + 7, 0
    if ataque == "Pisotón Goma Goma":
        return jugador.atk + 3, 0
    if ataque == "Ametralladora":
        return jugador.atk + 10, 5
    return jugador.atk, 0


def turno_jugador(jugador: Jugador, enemigo: Personaje) -> bool:
    """Retorna True si el jugador esquivó con Saltar."""
    opciones = [
        "Atacar",
        "Saltar 🦘 (50% esquivar)",
        "Cerebro 🧠 (analizar enemigo)",
    ]
    accion = elegir_opcion("Tu turno:", opciones)

    if accion == 0:
        ataques = ["Pistola Goma Goma", "Pisotón Goma Goma", "Ametralladora"]
        idx_ataque = elegir_opcion("Elige ataque:", ataques)
        nombre_ataque = ataques[idx_ataque]

        danio_base, costo = dano_ataque_luffy(jugador, nombre_ataque)
        if jugador.stamina < costo:
            print("No tienes stamina suficiente. Usas Pistola Goma Goma por defecto.")
            nombre_ataque = "Pistola Goma Goma"
            danio_base, costo = dano_ataque_luffy(jugador, nombre_ataque)

        jugador.stamina -= costo
        variacion = random.randint(-2, 4)
        danio_final = max(1, danio_base + variacion)
        danio_real = enemigo.recibir_danio(danio_final)
        print(f"\nLUFFY: ¡{nombre_ataque.upper()}!")
        print(f"➡️  {enemigo.nombre} recibe {danio_real} de daño.")
        return False

    if accion == 1:
        exito = random.random() < 0.5
        if exito:
            print("\n¡Luffy salta y prepara una esquiva!")
        else:
            print("\nLuffy intenta saltar, pero queda desbalanceado.")
        return exito

    # Cerebro
    print(f"\n🧠 Análisis de combate: {enemigo.nombre}")
    print(f"HP actual: {enemigo.hp}/{enemigo.hp_max}")
    print("Consejo: usa Ametralladora para rematar, Saltar cuando el jefe cargue.")
    return False


def turno_enemigo(enemigo: Personaje, jugador: Jugador, nombre_ataque: str, danio_base: int, esquivado: bool) -> None:
    if esquivado:
        print(f"{enemigo.nombre} usa {nombre_ataque}, pero Luffy lo esquiva. ❌")
        return

    variacion = random.randint(-2, 3)
    danio = max(1, danio_base + variacion)
    real = jugador.recibir_danio(danio)
    print(f"{enemigo.nombre} usa {nombre_ataque}.")
    print(f"💥 Luffy recibe {real} de daño.")


def combate(jugador: Jugador, enemigo: Personaje, ataque_enemigo: tuple[str, int], xp_recompensa: int) -> bool:
    titulo(f"⚔️ COMBATE INICIADO: LUFFY VS {enemigo.nombre.upper()}")
    while jugador.vivo() and enemigo.vivo():
        print(f"\n{jugador.estado()} | STAM {jugador.stamina}")
        print(f"{enemigo.nombre}: HP {enemigo.hp}/{enemigo.hp_max}")

        esquivado = turno_jugador(jugador, enemigo)
        if not enemigo.vivo():
            break

        nom_ataque, danio_base = ataque_enemigo
        turno_enemigo(enemigo, jugador, nom_ataque, danio_base, esquivado)

        # Regeneración ligera de stamina por turno
        jugador.stamina = min(30, jugador.stamina + 2)

    if jugador.vivo():
        titulo(f"✅ Victoria contra {enemigo.nombre}")
        jugador.ganar_xp(xp_recompensa)
        return True

    titulo("💀 Derrota")
    return False


# ---------- Historia ----------


def prologo() -> None:
    titulo("🏴‍☠️ ONE PIECE: ROMANCE DAWN")
    narrador("Pantalla negra. Se escucha el mar...")
    pausa(0.9)
    for linea in [
        "LA RIQUEZA... LA FAMA... EL PODER...",
        "GOL D. ROGER, EL REY DE LOS PIRATAS, alcanzó todo lo que este mundo tiene para ofrecer...",
        "¿Mi tesoro? Si lo quieren, es suyo. ¡Búsquenlo! ¡Lo dejé todo en ese lugar!",
        "Y así comenzó... LA GRAN ERA DE LOS PIRATAS.",
    ]:
        print(f"\n\"{linea}\"")
        pausa(1.1)


def escena_shanks() -> None:
    titulo("🌴 VILLA FOOSHA — 10 AÑOS ATRÁS")
    dialogo("LUFFY", "¡Shanks! ¡Llévame contigo! ¡Quiero ser pirata!")
    dialogo("SHANKS", "¿Tú? ¿Pirata? No puedes ni nadar.")
    narrador("Luffy se apuñala la mejilla para demostrar valor.")
    dialogo("SHANKS", "Ser pirata no se trata de hacerse daño para impresionar a otros.")
    narrador("Luffy muerde una Fruta del Diablo y su brazo se estira.")
    dialogo("SHANKS", "Ahora eres un hombre de goma... y nunca más podrás nadar.")

    narrador("Higuma secuestra a Luffy y aparece el Rey Marino.")
    dialogo("LUFFY", "¡SHANKS!")
    dialogo("SHANKS", "Lárgate.")
    narrador("Shanks pierde el brazo izquierdo y entrega su sombrero.")
    dialogo("SHANKS", "Devuélvemelo cuando te conviertas en un gran pirata.")
    dialogo("LUFFY", "¡Lo prometo! ¡Seré el Rey de los Piratas!")


def escena_barril(jugador: Jugador) -> bool:
    titulo("⛵ 10 AÑOS DESPUÉS — BARCO DE ALVIDA")
    dialogo("LUFFY", "Primero necesito al menos diez compañeros.")
    narrador("Luffy despierta en un barril, rodeado de piratas.")
    dialogo("ALVIDA", "¿Quién es el más hermoso del mar?")
    dialogo("KOBY", "T-Tú... capitana.")
    dialogo("LUFFY", "Yo no veo a nadie hermosa aquí.")

    enemigo1 = Personaje("Marino Pirata", hp_max=40, hp=40, atk=10, defensa=0)
    ok = combate(jugador, enemigo1, ("Garrotazo Pirata", 10), xp_recompensa=10)
    if not ok:
        return False

    dialogo("ALVIDA", "¡¿QUÉ DIJISTE?!")
    _ = elegir_opcion(
        "Elige diálogo:",
        [
            "❤️ Puño — ¡Nadie me importa!",
            "🧠 Cerebro — No vine por ti.",
        ],
    )

    alvida = Personaje("Alvida", hp_max=120, hp=120, atk=18, defensa=1)
    ok = combate(jugador, alvida, ("Maza de Hierro Destructor", 18), xp_recompensa=10)
    if not ok:
        return False

    dialogo("KOBY", "¡Quiero entrar a la Marina!")
    dialogo("LUFFY", "Entonces hazlo.")
    return True


def escena_shells_town(jugador: Jugador) -> bool:
    titulo("🏛️ SHELLS TOWN")
    narrador("Zoro está atado. Rika intenta ayudarlo con onigiri.")
    dialogo("LUFFY", "Únete a mi tripulación.")
    dialogo("ZORO", "Prefiero morir.")

    elegir_opcion(
        "Respuesta de Luffy:",
        [
            "🥊 Puño — Si estorbas, te dejaré.",
            "❤️ Corazón — Respeto tu sueño.",
            "🧠 Cerebro — Necesito al mejor espadachín para conquistar el Grand Line.",
        ],
    )

    narrador("Luffy recupera las tres espadas y comienza el combate contra Morgan.")
    morgan = Personaje("Morgan", hp_max=150, hp=150, atk=30, defensa=2)
    ok = combate(jugador, morgan, ("Hacha Vertical", 30), xp_recompensa=20)
    if not ok:
        return False

    dialogo("ZORO", "Si voy a morir... será luchando.")
    narrador("👒 NUEVO TRIPULANTE DESBLOQUEADO: ZORO (+100 XP)")
    jugador.ganar_xp(100)
    return True


def ending(jugador: Jugador) -> None:
    titulo("🎬 FIN DE ROMANCE DAWN")
    print(jugador.estado())
    narrador("Así comenzó la leyenda del hombre que sería Rey de los Piratas.")


# ---------- Main ----------


def main() -> int:
    random.seed()
    jugador = Jugador(
        nombre="Monkey D. Luffy",
        hp_max=100,
        hp=100,
        atk=15,
        defensa=10,
        nivel=1,
        xp=0,
        xp_objetivo=10,
        stamina=20,
    )

    prologo()
    escena_shanks()

    if not escena_barril(jugador):
        print("\nGame Over. Inténtalo de nuevo, futuro Rey de los Piratas.")
        return 1

    if not escena_shells_town(jugador):
        print("\nGame Over en Shells Town.")
        return 1

    ending(jugador)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nJuego interrumpido.")
        raise SystemExit(130)
