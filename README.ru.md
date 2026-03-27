# UPS-Lite Patch Bundle

Проект возвращает поддержку плагина `ups_lite.py` для плат XiaoJ/ACE UPS Lite с чипом `0x62` (`CW2015`) и предотвращает ложные выключения из-за невалидных 0-read

<img src="https://github.com/sigdevel/ups_lite_repair/blob/master/2026-03-27_15-25.png?raw=true"
     alt="screen"
     width="25%">

Файлы:

- `ups_lite.py` - текущая модифицированная версия оригинального плагина  
  https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
- `ups_lite.patch` - unified diff относительно исходного `ups_lite.py`  
  https://github.com/evilsocket/pwnagotchi/blob/master/pwnagotchi/plugins/default/ups_lite.py
- `apply_patch.py` - безопасный скрипт для применения патча к исходному файлу

Что меняет патч:

- автоопределение `0x62 / cw2015` и `0x36 / max17040`
- инициализацию `CW2015`
- корректное чтение `voltage` и `capacity` для `0x62`
- защиту от ложного shutdown, если чтение батареи невалидно

Ожидаемый исходный файл:

- `/usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py`

1. Применение через скрипт:

```bash
cd /path/to/ups_lite_repair
sudo python3 apply_patch.py
```

2. Абсолютный путь:

```bash
sudo python3 apply_patch.py /usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py
```

Что делает скрипт:

- проверяет, что целевой файл совпадает с ожидаемой исходной версией
- создаёт резервную копию рядом с целевым файлом: `ups_lite.py.bak`
- записывает патченую версию

Ручное применение patch-файла:

```bash
sudo patch /usr/local/lib/python3.7/dist-packages/pwnagotchi/plugins/default/ups_lite.py < ups_lite.patch
```
