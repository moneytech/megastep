from rebar import arrdict
from megastep import modules, core, toys, scene
from torch import nn
from megastep.demo import heads


class Minimal:

    def __init__(self, n_envs=1):
        """A minimal environment, with a box env, depth observations and simple movement. A good foundation for
        building your own environments. See :ref:`the simple environment tutorial for details <minimal-env>`"""

        geometries = n_envs*[toys.box()]
        scenery = scene.scenery(geometries, n_agents=1)
        self.core = core.Core(scenery)
        self.spawner = modules.RandomSpawns(geometries, self.core)
        self.rgb = modules.RGB(self.core)
        self.movement = modules.SimpleMovement(self.core)

        self.obs_space = self.rgb.space
        self.action_space = self.movement.space

    def reset(self):
        self.spawner(self.core.agent_full(True))
        return arrdict.arrdict(obs=self.rgb())

    def step(self, decision):
        self.movement(decision)
        return arrdict.arrdict(obs=self.rgb())

class Agent(nn.Module):

    def __init__(self, env, width=32):
        super().__init__()
        self.intake = heads.intake(env.obs_space, width)
        self.output = heads.output(env.action_space, width)
        self.policy = nn.Sequential(self.intake, self.output)
        
    def forward(self, world):
        logits = self.policy(world.obs)
        actions = self.output.sample(logits)
        return arrdict.arrdict(logits=logits, actions=actions)