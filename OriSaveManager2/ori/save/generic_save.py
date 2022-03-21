from uuid import UUID

from ori.save.buffer import Buffer


SAVE_HEADER_FORMAT = """
    string  area_name
    int     completion
    int     health
    int     max_health
    int     energy
    int     max_energy
    time    time
    int     progression
    bool    is_completed
    uuid    uuid
    bool    is_debug_on
    int     order
    int     difficulty
    bool    was_killed
    bool    completed_with_everything
    int     lowest_difficulty
    bool    is_trial_save
"""

SAVE_HEADER_FORMAT = [ row.split() for row in SAVE_HEADER_FORMAT.split('\n') if row.strip() ]


class GenericSave:
    def __init__(self, *, path=None, buffer=None):
        if sum(x is not None for x in [path, buffer]) != 1:
            raise Exception('Provide either path or buffer.')

        if path is not None:
            with open(path, 'rb') as fd:
                buffer = fd.read()
        
        self._buffer = Buffer(buffer)
        self._read_header()
        self._scenes = None

    def _check(self, value_type, expected_value):
        value = getattr(self._buffer, f'pop_{value_type}')()

        if value != expected_value:
            raise Exception(f'Invalid File Format: "{value}" != "{expected_value}".')

    def _read_header(self):
        self._check('string', b'OriSave')  # File Header
        self._check('int', 13)  # File Version

        for data_type, data_name in SAVE_HEADER_FORMAT:
            pop_func = getattr(self._buffer, 'pop_{}'.format(data_type))
            setattr(self, data_name, pop_func())

        self._check('string', b'SaveGameData')  # File Format
        self._check('int', 1)  # Data Version

    def _read_scenes(self):
        count, = self._buffer.pop('i')
        for _ in range(count):
            uuid = self._buffer.pop_uuid()
            data = self._buffer.pop_string('I')
            yield uuid, data

    def _read_scene_collections(self):
        count, = self._buffer.pop('i')
        for _ in range(count):
            uuid = self._buffer.pop_uuid()
            scene = dict(self._read_scenes())
            yield uuid, scene

    def _read_content(self):
        self._scenes = dict(self._read_scene_collections())
        self._buffer = None

    def object(self, scene_id, object_id):
        if self._scenes is None:
            self._read_content()

        return self._scenes.get(UUID(scene_id), {}).get(UUID(object_id))

    def print(self):
        for _, data_name in SAVE_HEADER_FORMAT:
            print(data_name, getattr(self, data_name))

        print()
