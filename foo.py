class MurderKittenCommand:

    def __init__(self, kitten_id, implement):
        pass


class MurderKittenCommandHandler:

    def __call__(self, cmd):
        with self.uow.start() as tx:
            kitten = tx.kittens.get(cmd.kittenid)
            kitten.murder_with(cmd.implement)
            tx.commit()

