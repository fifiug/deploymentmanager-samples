# Copyright 2016 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Creates a Compute Instance with the provided metadata."""


COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'


def GlobalComputeUrl(project, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/global/', collection, '/', name])


def ZonalComputeUrl(project, zone, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/zones/', zone, '/', collection, '/', name])


def GenerateConfig(context):
  """Generate configuration."""

  name_prefix = context.env['deployment'] + '-' + context.env['name']

  instance_properties = {
      'zone': context.properties['zone'],
      'machineType': ZonalComputeUrl(
          context.env['project'], context.properties['zone'], 'machineTypes',
          'f1-micro'),
      'metadata': {
          'items': [{
              'key': 'startup-script',
              'value': context.properties['startup-script']
          }]
      },
      'disks': [{
          'deviceName': 'boot',
          'type': 'PERSISTENT',
          'autoDelete': True,
          'boot': True,
          'initializeParams': {
              'diskName': name_prefix + '-disk',
              'sourceImage': GlobalComputeUrl(
                  'debian-cloud', 'images', 'family/debian-9'
                  )
              },
          }],
      'networkInterfaces': [{
          'accessConfigs': [{
              'name': 'External NAT',
              'type': 'ONE_TO_ONE_NAT'
              }],
          'network': GlobalComputeUrl(
              context.env['project'], 'networks', 'default')
          }]
      }

  instance = {
          'name': name_prefix ,
          'type': 'compute.v1.instance',
          'properties': instance_properties
          }
      
  resources= [
    {
      'name': 'removeAccessConfig',
      'action': 'gcp-types/compute-beta:compute.instances.deleteAccessConfig',
      'metadata': {
          'runtimePolicy': ['UPDATE_ALWAYS'],

      },
      'properties': {
          'instance': '$(ref.{}.name)'.format(name_prefix),
          'networkInterface' : '$(ref.{}.networkInterfaces[0].name)'.format(name_prefix),
          'zone': context.properties['zone'],
          'accessConfig': 'External NAT'
         }
      }
,
           {
      'name': 'addaccessConfig',
      'action': 'gcp-types/compute-beta:compute.instances.addAccessConfig',
      'metadata': {
          'runtimePolicy': ['UPDATE_ALWAYS'],
          'dependsOn': [ 'removeAccessConfig' ]
      },
      'properties': {
          'instance': '$(ref.{}.name)'.format(name_prefix),
          'networkInterface' : '$(ref.{}.networkInterfaces[0].name)'.format(name_prefix),
          'zone': context.properties['zone'],
          'name': 'External NAT',
          'type': 'ONE_TO_ONE_NAT',
          'natIP': context.properties['natIP'] #new natIP
   }
      }
    ] 
  resources.append(instance)
  # Resources to return.
  resources = {
      'resources': resources
      }

  return resources
