from flask_restful import Resource, reqparse

from flask_jwt_extended import (
    get_jwt_identity,
    get_raw_jwt,
    jwt_required,
    get_jwt_claims,
    jwt_optional
)

from models.withdrawRequest import WithdrawRequestModel
from models.user import UserModel
from blacklist import BLACKLIST

class all_withdrawRequest(Resource):
    @jwt_required
    def get(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401

        return {'withdraw_request': list(map(lambda x: x.json(), WithdrawRequestModel.find_all()))}

class verifyWithdraw(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('req_id',
                        type = int,
                        required = True,
                        help = "req_id (required) error"
                        )
    @jwt_required
    def post(self):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'Admin privilege required.'}, 401
        data = verifyWithdraw.parser.parse_args()
        req = WithdrawRequestModel.find_by_id(data['req_id'])
        if req:
            user = UserModel.find_by_id(req.user_id)
        else:
            return {'error':'user request not found'}

        user.invest_amt = user.invest_amt-req.amount
        user.save_to_db()
        req.delete_from_db()
        return user.json()
