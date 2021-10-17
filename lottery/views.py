# IMPORTS
import copy
import logging

from flask import Blueprint, render_template, request, flash
from sqlalchemy import desc
from app import db
from models import Draw, User


user = User.query.first()
draw_key = user.draw_key

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
def lottery():
    draws = Draw.query.order_by(desc('id')).all()

    draws_copies = list(map(lambda x: copy.deepcopy(x), draws))

    decrypted_draws = []

    for d in draws_copies:
        d.view_draw(draw_key)
        decrypted_draws.append(d)

    return render_template('lottery.html', draws=decrypted_draws)


@lottery_blueprint.route('/add_draw', methods=['POST'])
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    submitted_draw.strip()

    # create a new draw with the form data.
    new_draw = Draw(user_id=user.id, draw=submitted_draw, win=False,
                  round=0, draw_key=draw_key)  # TODO:  Done update user_id [user_id=1 is a placeholder]
    # add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
def view_draws():
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(played=False, id=user.id).all()  # TODO:  Done filter playable draws for current user

    # if playable draws exist
    if len(playable_draws) != 0:
        # re-render lottery page with playable draws

        draws_copies = list(map(lambda x: copy.deepcopy(x), playable_draws))

        decrypted_draws = []

        for d in draws_copies:
            d.view_draw(draw_key)
            decrypted_draws.append(d)

        return render_template('lottery.html', playable_draws=decrypted_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():
    # get played draws
    played_draws = Draw.query.filter_by(played=True, id=user.id).all()  # TODO:  Done filter played draws for current user

    # if played draws exist
    if len(played_draws) != 0:
        draws_copies = list(map(lambda x: copy.deepcopy(x), played_draws))

        decrypted_draws = []

        for d in draws_copies:
            d.view_draw(draw_key)
            decrypted_draws.append(d)
        return render_template('lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
def play_again():
    delete_played = Draw.__table__.delete().where(Draw.played, id=user.id)  # TODO:  Done delete played draws for current user only
    db.session.execute(delete_played)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()
