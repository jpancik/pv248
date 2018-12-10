import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse


def get_param(params, key, default=''):
    if key in params:
        value = params[key]
        if len(value) > 0:
            return value[0]
    return default


def get_param_int(params, key):
    if key in params:
        value = params[key]
        if len(value) > 0:
            try:
                return int(value[0])
            except ValueError:
                pass
    return None


class GamesManager(object):
    def __init__(self):
        self.games = {}
        self.id = 0

    def start_game(self, name):
        game_id = self.id
        self.id += 1

        board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]

        game = {
            'id': game_id,
            'name': name,
            'board': board,
            'next_player': 1
        }

        self.games[game_id] = game
        return {
            'id': int(game_id)
        }

    def is_game(self, game_id):
        return game_id in self.games

    def can_be_played(self, game_id, player_id):
        return self.is_game(game_id) and self.games[game_id]['next_player'] == player_id

    def is_finished(self, game_id):
        board = self.games[game_id]['board']

        is_draw = True
        for row in self.games[game_id]['board']:
            for cell in row:
                if cell == 0:
                    is_draw = False

        return is_draw or self.is_winner(board, 1) or self.is_winner(board, 2)

    def play(self, game_id, player_id, x, y):
        if self.can_be_played(game_id, player_id):
            game = self.games[game_id]

            if x < 0 or x >= 3 or y < 0 or y >= 3:
                return False

            if game['board'][y][x] != 0:
                return False

            game['board'][y][x] = player_id
            game['next_player'] += 1
            if game['next_player'] > 2:
                game['next_player'] = 1

            return True
        else:
            return False


    @staticmethod
    def is_winner(board, player):
        for x in range(3):
            for y in range(3):
                delta_x = [-1, 1, 0, 0, 1, 1]
                delta_y = [0, 0, 1, -1, 1, -1]

                if board[y][x] == player:
                    for i in range(6):
                        new_x_1 = x + delta_x[i]
                        new_y_1 = y + delta_y[i]
                        new_x_2 = x - delta_x[i]
                        new_y_2 = y - delta_y[i]

                        if new_x_1 < 0 or new_x_1 >= 3 or new_x_2 < 0 or new_x_2 >= 3\
                                or new_y_1 < 0 or new_y_1 >= 3 or new_y_2 < 0 or new_y_2 >= 3:
                            continue

                        if board[new_y_1][new_x_1] == player and board[new_y_2][new_x_2] == player:
                            return True

        return False

    def get_status(self, game_id):
        if not self.is_game(game_id):
            raise AssertionError('Game with id %s does not exist.' % game_id)

        game = self.games[game_id]

        if self.is_finished(game_id):
            winner = 0
            if self.is_winner(game['board'], 1):
                winner = 1
            if self.is_winner(game['board'], 2):
                winner = 2
            return {
                'winner': int(winner)
            }
        else:
            return {
                'board': game['board'],
                'next': game['next_player']
            }


def main():
    if len(sys.argv) >= 2:
        input_port = int(sys.argv[1])
    else:
        print('You have to specify a port name as a first argument.')
        return

    games_manager = GamesManager()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_url = parse.urlparse(self.path)

            params = parse.parse_qs(parsed_url.query)

            if parsed_url.path == '/start' or parsed_url.path == '/start/':
                result = games_manager.start_game(get_param(params, 'name'))
                self.send_result(200, result)
            elif parsed_url.path == '/status' or parsed_url.path == '/status/':
                game_id = get_param_int(params, 'game')

                if game_id is not None:
                    if not games_manager.is_game(game_id):
                        self.send_result(400, {
                            'error': 'Game with id %s does not exist.' % game_id
                        })
                    else:
                        result = games_manager.get_status(game_id)
                        self.send_result(200, result)
                else:
                    self.send_result(400, {
                        'error': 'Game id is missing or not a number.'
                    })
            elif parsed_url.path == '/play' or parsed_url.path == '/play/':
                game_id = get_param_int(params, 'game')
                player_id = get_param_int(params, 'player')
                x = get_param_int(params, 'x')
                y = get_param_int(params, 'y')

                if game_id is not None and player_id is not None and x is not None and y is not None:
                    if not games_manager.is_game(game_id):
                        self.send_result(400, {
                            'status': 'bad',
                            'message': 'Game with id %s does not exist.' % game_id
                        })
                        return

                    if games_manager.is_finished(game_id):
                        self.send_result(200, {
                            'status': 'bad',
                            'message': 'Game with id %s is finished.' % game_id
                        })
                        return

                    if player_id != 1 and player_id != 2:
                        self.send_result(200, {
                            'status': 'bad',
                            'message': 'Player id has to be either 1 or 2.'
                        })
                        return

                    if not games_manager.can_be_played(game_id, player_id):
                        self.send_result(200, {
                            'status': 'bad',
                            'message': 'It\'s not player\'s %s turn.' % player_id
                        })
                        return

                    if games_manager.play(game_id, player_id, x, y):
                        self.send_result(200, {
                            'status': 'ok'
                        })
                    else:
                        self.send_result(200, {
                            'status': 'bad',
                            'message': 'Parameter x or y is out of bounds or there is not 0 on the x,y position. Allowed numbers are [0,1,2].'
                        })
                else:
                    self.send_result(400, {
                        'status': 'bad',
                        'message': 'One or more of the parameters {game, player, x, y} is/are missing or is/are not integer.'
                    })
            else:
                self.send_result(404, {
                    'error': 'Unknown GET path.'
                })

        def send_result(self, status_code, content):
            data = json.dumps(content)

            self.send_response(status_code)

            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()

            self.wfile.write(bytes(data, 'UTF-8'))

    server = HTTPServer(('', input_port), Handler)
    server.serve_forever()


main()