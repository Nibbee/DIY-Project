from distutils import errors
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required, jwt_optional
from http import HTTPStatus

from models.instruction import Instruction

from schemas.instruction import InstructionSchema

instruction_schema = InstructionSchema()
instruction_list_schema = InstructionSchema(many=True)

class InstructionListResource(Resource):

    def get(self):

        instructions = Instruction.get_all_published()

        return instruction_list_schema.dump(instructions).data, HTTPStatus.OK

    @jwt_required
    def post(self):
        json_data = request.get_json()

        current_user = get_jwt_identity()

        data, errors = instruction_schema.load(data=json_data)

        if errors:
            return {'message': 'Validation errors', 'errors': errors}, HTTPStatus.BAD_REQUEST

        instruction = Instruction(**data)
        instruction.user_id = current_user
        instruction.save()

        return instruction_schema.dump(instruction).data, HTTPStatus.CREATED


class InstructionResource(Resource):

    @jwt_optional
    def get(self, instruction_id):
        instruction = Instruction.get_by_id(instruction_id=instruction_id)
        
        if instruction is None:
            return {"message": "instruction not found"}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if instruction.is_publish == False and instruction.user_id != current_user:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        return instruction.data, HTTPStatus.OK

    @jwt_required
    def put(self, instruction_id):
        json_data = request.get_json()

        instruction = Instruction.get_by_id(instruction_id=instruction_id)

        if instruction is None:
            return {'message': 'instruction not found'}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != instruction.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        instruction.name = json_data['name']
        instruction.description = json_data['description']
        instruction.steps = json_data['steps']
        instruction.tools = json_data['tools']
        instruction.cost = json_data['cost']
        instruction.duration = json_data['duration']

        instruction.save

        return instruction.data, HTTPStatus.OK

    @jwt_required
    def delete(self, instruction_id):

        instruction = Instruction.get_by_id(instruction_id=instruction_id)
        

        if instruction is None:
            return {"message": "instruction not found"}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != instruction.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        instruction.delete()

        return {}, HTTPStatus.NO_CONTENT


class InstructionPublishResource(Resource):

    @jwt_required
    def put(self, instruction_id):

        instruction = Instruction.get_by_id(instruction_id=instruction_id)

        if instruction is None:
            return {"message": "instruction not found"}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != instruction.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        instruction.is_publish = True
        instruction.save()

        return {}, HTTPStatus.NO_CONTENT

    @jwt_required
    def delete(self, instruction_id):

        instruction = Instruction.get_by_id(instruction_id=instruction_id)

        if instruction is None:
            return {'message': 'Instruction not found'}, HTTPStatus.NOT_FOUND

        current_user = get_jwt_identity()

        if current_user != instruction.user_id:
            return {'message': 'Access is not allowed'}, HTTPStatus.FORBIDDEN

        instruction.is_publish = False
        instruction.save()

        return {}, HTTPStatus.NO_CONTENT
