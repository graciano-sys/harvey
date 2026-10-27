"""Prospects who read and write Spanish (icp.language: es): searches ask for
Spanish results in their country, emails are written in Spanish, and owners
are found on Spanish-language sites."""

from types import SimpleNamespace

from harvey.collectors import discover as D
from harvey.collectors import people as P
from harvey.config import accept_language, load_config, writing_language_rule


def _es_config():
    config = load_config()
    config.icp.language = "es"
    config.icp.country = "mx"
    config.icp.geography = ["Monterrey, NL"]
    config.icp.geo_coordinates = {"Monterrey, NL": "25.6866,-100.3161,30"}
    return config


# ── writing ──

def test_english_prompts_get_no_language_block():
    assert writing_language_rule(load_config()) == ""


def test_spanish_prompts_ask_for_mexican_spanish_with_the_same_rules():
    rule = writing_language_rule(_es_config())
    assert "Mexican Spanish" in rule and "usted" in rule
    assert "gratis" in rule and "{{first_name}}" in rule


def test_an_unlisted_language_is_still_named():
    config = load_config()
    config.icp.language = "PT"
    assert 'code "pt"' in writing_language_rule(config)


# ── searching ──

def test_queries_carry_the_language_and_country():
    queries = D.build_queries(_es_config())
    assert queries and all(q.language == "es" and q.country == "mx" for q in queries)
    assert queries[0].coordinate == "25.6866,-100.3161,30"


def test_a_search_with_no_place_is_a_search_in_the_icp_country():
    q = D.DiscoveryQuery(term="inmobiliaria", language="es", country="mx")
    assert D._dfs_location(q, "13z") == {"location_code": 2484}
    assert D._dfs_location(D.DiscoveryQuery(term="roofer"), "13z") == {"location_code": 2840}


def test_serper_gets_hl_and_gl_only_when_not_english_us():
    assert D.serper_locale("en", "") == {}
    assert D.serper_locale("en", "us") == {}
    assert D.serper_locale("es", "mx") == {"hl": "es", "gl": "mx"}


def test_sites_are_read_in_the_prospects_language():
    assert accept_language(load_config()) == "en-US,en;q=0.9"
    assert accept_language(_es_config()) == "es-MX,es;q=0.9,en;q=0.5"


def test_scout_tries_spanish_pages_first_on_a_spanish_icp():
    from harvey.agents.scout import FALLBACK_SITE_PATHS, Scout
    es = SimpleNamespace(config=_es_config())
    es._search_locale = lambda: Scout._search_locale(es)
    assert Scout._fallback_paths(es)[0] == "/nosotros"
    en = SimpleNamespace(config=load_config())
    en._search_locale = lambda: Scout._search_locale(en)
    assert Scout._fallback_paths(en) == FALLBACK_SITE_PATHS


# ── finding the owner ──

def test_accented_names_and_spanish_honorifics():
    assert P.split_person_name("Lic. José Núñez") == ("José", "Núñez")
    assert P.split_person_name("Ing. María de la Cruz") == ("María", "de la Cruz")
    assert P.split_person_name("Equipo Comercial") is None
    assert P.split_person_name("Nuestro Equipo") is None


def test_spanish_owner_titles():
    for title in ("Director General", "Dueña", "Fundadora y Directora", "Propietario",
                  "Socio Director", "Presidenta"):
        assert P.is_owner_title(title), title
    for title in ("Vicepresidente", "Asistente de Dirección General", "Asesor inmobiliario",
                  "Fundador (1952-2001)", "Fundador, fallecido"):
        assert not P.is_owner_title(title), title


def test_owners_named_in_spanish_prose():
    html = ("<p>Inmobiliaria fundada en 2004 por la Lic. Ana Ruiz Soto.</p>"
            "<p>Nuestro director general, Luis Peña, atiende cada caso. ¿Busca oficina?</p>"
            "<p>Hola, sácame de dudas.</p>")
    found = {p["full_name"]: p for p in P.people_from_prose(html, "ejemplo.example", "Ejemplo")}
    assert set(found) == {"Ana Ruiz Soto", "Luis Peña"}
    assert all(p["owner"] for p in found.values())


def test_spanish_team_cards():
    team = ('<div class="team"><h3>José Núñez</h3><p>Director General</p>'
            "<h3>Carla Ibáñez</h3><p>Asesora inmobiliaria</p>"
            "<h3>Rosa Díaz</h3><p>Fundadora de Otra Empresa</p>"
            "<h3>Equipo Comercial</h3><p>Ventas</p></div>")
    found = {p["full_name"]: p for p in
             P.find_people([("https://ejemplo.example/nosotros", team)], "ejemplo.example", "Ejemplo")}
    assert found["José Núñez"]["owner"] is True
    assert found["Carla Ibáñez"]["owner"] is False
    # A customer's own company, as in a testimonial, is not this business.
    assert "Rosa Díaz" not in found and "Equipo Comercial" not in found


def test_spanish_menu_links_are_followed():
    nav = ('<a href="/nosotros">Nosotros</a><a href="/propiedades">Propiedades</a>'
           '<a href="/quienes-somos">Quiénes somos</a><a href="/contacto">Contacto</a>')
    links = P.menu_links(nav, "https://ejemplo.example/")
    assert links[-1] == "https://ejemplo.example/contacto"
    assert set(links) == {"https://ejemplo.example/nosotros",
                          "https://ejemplo.example/quienes-somos",
                          "https://ejemplo.example/contacto"}
