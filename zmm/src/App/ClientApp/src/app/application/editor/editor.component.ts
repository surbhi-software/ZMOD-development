import { Component, OnInit, ViewEncapsulation, Input, OnChanges } from '@angular/core';
import { ApiRoutes, HttpService, UtilService } from '../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class EditorComponent implements OnInit, OnChanges {
  @Input() modelArchitecture: any = {};
  @Input() selectedModel: any = {};
  public selectedLayer: any = {};
  public sideBarItems: any[] = [];
  public layerError;
  public sideBarGeneralItems: any[] = [
    {
      'name': 'Section',
      'layerId': 'NA',
      'children': [] as any[],
      'itemType': 'FOLDING',
      'icon': 'mdi mdi-group',
      'class': 'wide'
    },
    {
      'name': 'Data',
      'icon': 'mdi mdi-database-plus',
      'itemType': 'DATA',
      'layerId': 'Data',
      'trainable': true
    },
    {
      'name': 'Code',
      'icon': 'mdi mdi-code-braces',
      'itemType': 'CODE',
      'layerId': 'Code',
      'trainable': true
    }
  ];
  public targetItems: any[] = [];
  public filterConfig: any = {};
  public isLoading = false;
  public showFilter = false;
  public panelOpenState = false;
  public flatLayers: any[] = [];

  public tempLayersData = {
    'layerinfo': [
      {
        'layerGroup': 'Standard Layer',
        'icon': 'mdi mdi-layers',
        'layers': [
          {
            'name': 'Input',
            'layerType': 'Input',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'Dense',
            'layerType': 'Dense',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'activationFunction',
                'label': 'Activation Function',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'tanh',
                  'relu',
                  'sigmoid'
                ],
                'dataType': 'string',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'units',
                'label': 'Units',
                'value': 'Linear',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Fully connected layer'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'options': [
                ],
                'hint': 'only required if dragged first',
                'dataType': 'int'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'Dropout',
            'layerType': 'Dropout',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'dropoutRate',
                'label': 'dropoutRate',
                'value': '',
                'options': [
                ],
                'dataType': 'float',
                'hint': 'Value between 0 to 1'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'options': [
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'Flatten',
            'layerType': 'Flatten',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'data_format',
                'label': 'data_format',
                'value': 'channels_last',
                'options': [
                  'channels_last',
                  'channels_first'
                ],
                'dataType': 'string',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'options': [
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'BatchNormalization',
            'layerType': 'BatchNormalization',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'batchNormalizationEpsilon',
                'label': 'batchNormalizationEpsilon',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'batchNormalizationAxis',
                'label': 'batchNormalizationAxis',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'batchNormalizationScale',
                'label': 'batchNormalizationScale',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          }
        ]
      },
      {
        'layerGroup': 'Activation Layer',
        'icon': 'mdi mdi-layers',
        'layers': [
          {
            'name': 'Softmax',
            'layerType': 'Activation',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'activationFunction',
                'label': 'activationFunction',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'Relu',
            'layerType': 'Activation',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'activationFunction',
                'label': 'activationFunction',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'reLu6',
            'layerType': 'Activation',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'activationFunction',
                'label': 'activationFunction',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          }
        ]
      },
      {
        'layerGroup': 'CNN Layer',
        'icon': 'mdi mdi-layers',
        'layers': [
          {
            'name': 'Conv2D',
            'layerType': 'Conv2D',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'featureMaps',
                'label': 'featureMaps',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'kernel',
                'label': 'kernel',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'paddingType',
                'label': 'paddingType',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'stride',
                'label': 'stride',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'dilationRate',
                'label': 'dilationRate',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'DepthwiseConv2D',
            'layerType': 'DepthwiseConv2D',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'activationFunction',
                'label': 'activationFunction',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'kernel',
                'label': 'kernel',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'paddingType',
                'label': 'paddingType',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'stride',
                'label': 'stride',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'dilationRate',
                'label': 'dilationRate',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'activationFunction',
                'label': 'activationFunction',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'ZeroPadding1D',
            'layerType': 'ZeroPadding1D',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'paddingDims',
                'label': 'paddingDims',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'ZeroPadding2D',
            'layerType': 'ZeroPadding2D',
            'itemType': 'LAYER',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'properties': [
              {
                'id': 'paddingDims',
                'label': 'paddingDims',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          },
          {
            'name': 'ZeroPadding3D',
            'layerType': 'ZeroPadding3D',
            'connectionLayerId': 'NA',
            'layerId': 'NA',
            'itemType': 'LAYER',
            'properties': [
              {
                'id': 'paddingDims',
                'label': 'paddingDims',
                'value': 'Linear',
                'options': [
                  'Linear',
                  'Option 2'
                ],
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'inputDimension',
                'label': 'inputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              },
              {
                'id': 'outputDimension',
                'label': 'outputDimension',
                'value': '',
                'dataType': 'int',
                'hint': 'Some instructions ...'
              }
            ]
          }
        ]
      },
      {
        'icon': 'mdi mdi-layers',
        'layerGroup': 'Templates',
        'layers': [
          {
            'itemType': 'TEMPLATE',
            'templateId': 'NA',
            'name': 'Name of the template 1'
          },
          {
            'itemType': 'TEMPLATE',
            'templateId': 'NA',
            'name': 'Name of the template 2'
          },
          {
            'itemType': 'TEMPLATE',
            'templateId': 'NA',
            'name': 'Name of the template 3'
          }
        ]
      }
    ]
  };

  constructor(private apiService: HttpService, private utilService: UtilService) { }

  public getLayers() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelGetLayers)
      .pipe(finalize(() => {
        this.isLoading = false;
      }))
      .subscribe(data => {
        this.sideBarItems = data.layerinfo;
        // this.sideBarItems = this.tempLayersData.layerinfo;
      });
  }

  public onFilterDataSelection($event: any) {
    this.selectedLayer.layerId = $event.name;
    this.selectedLayer.url = $event.url;
    this.selectedLayer.filePath = $event.filePath;
    this.showFilter = false;
    this.updateLayer(this.selectedLayer);
  }

  public log(e: any) {
    console.log(e.type);
  }

  public onLayerDrop($event: any, selectedSection?: any) {
    if (!$event.value.id) {
      $event.value.id = this.utilService.generateUniqueID();
    }
    if ($event.value.itemType === 'FOLDING' && !$event.value.sectionId) {
      $event.value.sectionId = this.utilService.generateUniqueID();
    }
    let listOfLayers = this.targetItems;
    if (selectedSection && selectedSection.id) {
      listOfLayers = selectedSection.children;
      $event.value.sectionId = selectedSection.sectionId;
      // Disable the addition of nested sections
      if ($event.value.itemType === 'FOLDING') {
        const filteredSectionObj = this.utilService.filterArray(listOfLayers, 'id', $event.value.id);
        return listOfLayers.splice(filteredSectionObj.index, 1);
      }
    } else if ($event.value.itemType !== 'FOLDING') {
      delete $event.value.sectionId;
    }
    this.getPreviousLayer($event.value);
    if ($event.value.layerId === 'NA') {
      $event.value.layerId = `${$event.value.name}_${this.flatLayers.length}`;
      if (this.selectedModel.modelGeneratedFrom === 'Workflow' && $event.value.layerId === 'Section_1') {
        $event.value.layerId = 'model1';
      }
      if (this.selectedModel.modelGeneratedFrom === 'Workflow' && $event.value.layerId === 'Section_2') {
        $event.value.layerId = 'model2';
      }
    }
    const filteredLayerObj = this.utilService.filterArray(listOfLayers, 'id', $event.value.id);
    if (filteredLayerObj.index !== -1) {
      $event.value.layerIndex = filteredLayerObj.index;
      if (filteredLayerObj.index > 0) {
        const previousLayer = listOfLayers[filteredLayerObj.index - 1];
        $event.value.connectionLayerId = previousLayer.layerId;
        if (selectedSection) {
          $event.value.connectionLayerId = selectedSection.connectionLayerId;
        }
      }
      this.updateLayer($event.value);
    }
  }

  public updateInputDimensionFromOutputDimension(selectedLayer: any) {
    const filteredLayerObj = this.getPreviousLayer(selectedLayer);
    const previousLayer = filteredLayerObj.previousLayer;
    if (previousLayer) {
      const previousLayerProp: any = this.utilService.filterArray(previousLayer.properties, 'id', 'outputDimension');
      const addedLayerProp: any = this.utilService.filterArray(selectedLayer.properties, 'id', 'inputDimension');
      if (previousLayerProp.index !== -1 && addedLayerProp.index !== -1) {
        addedLayerProp.item.value = previousLayerProp.item.value;
      }
    }
    this.updateLayer(selectedLayer);
  }

  public getPreviousLayer(layer: any): any {
    const selectedLayer = layer;
    this.flatLayers = [];
    let previousLayer = null;
    for (let layer of this.targetItems) {
      if (layer && layer.id) {
        this.flatLayers.push(layer);
        if (layer.children && layer.children.length) {
          const childrenLayers = layer.children;
          for (let childLayer of childrenLayers) {
            this.flatLayers.push(childLayer);
          }
        }
      }
    }

    const filteredLayer = this.utilService.filterArray(this.flatLayers, 'id', layer.id);
    if (filteredLayer.index > 0) {
      previousLayer = this.flatLayers[filteredLayer.index - 1];
    }
    console.log('previousLayer', previousLayer, 'filteredLayer', filteredLayer);
    return {
      'previousLayer': previousLayer,
      'filteredLayer': filteredLayer
    };
  }

  public onLayerRemove($event: any) {
    const options = {
      body: $event.value
    };
    this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.modelUpdateLayer(this.selectedModel.id), options)
      .subscribe(response => {
        this.selectedLayer = {};
      });
  }

  public selectLayer(data: any) {
    this.layerError = '';
    this.selectedLayer = data;
    this.showFilter = false;
    if ((this.selectedLayer.itemType === 'DATA' || this.selectedLayer.itemType === 'CODE') && !this.selectedLayer.url) {
      this.selectData();
    } else {
      this.updateInputDimensionFromOutputDimension(this.selectedLayer);
    }
  }

  public updateLayer(data: any) {
    const isTemplate = (data.itemType === 'TEMPLATE');
    this.isLoading = isTemplate;
    this.layerError = '';
    if (data.properties && data.properties.length) {
      data.properties.forEach(property => {
        if (!Array.isArray(property.value) && (property.dataType === 'array')) {
          property.value = property.value.split(',').map(Number).filter(x => !isNaN(x));
        } else if (property.dataType === 'integer') {
          property.value = parseInt(property.value);
        } else if (property.dataType === 'float') {
          property.value = parseFloat(property.value);
        }
      });
    }
    const options = {
      body: data
    };
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.modelUpdateLayer(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        if (isTemplate && response && response.architecture) {
          this.targetItems = response.architecture;
        } else if (response && response.layerUpdated) {
          data = response.layerUpdated;
          if (data.properties && data.properties.length) {
            data.properties.forEach(property => {
              if ((property.dataType === 'array') && Array.isArray(property.value)) {
                property.value = property.value.toString();
              }
            });
            this.targetItems.forEach(element => {
              if (element.id === data.id) {
                for (const i in element.properties) {
                  element.properties[i] = data.properties[i];
                }
              }
            });
          }
          if (response.layerUpdated && response.layerUpdated.errorMessage) {
            this.layerError = response.layerUpdated.errorMessage;
          }
        }
        if (response && response.errorMessage) {
          this.layerError = response.errorMessage;
        }
      });
  }

  public selectData() {
    this.showFilter = true;
    this.filterConfig = {
      route: this.selectedLayer.itemType.toLowerCase()
    };
  }

  public onPropertyUpdate() {
    this.updateLayer(this.selectedLayer);
  }

  public toggleLayerSection(selectedLayer: any) {
    selectedLayer.sectionCollapse = !selectedLayer.sectionCollapse;
    this.updateLayer(selectedLayer);
  }

  ngOnChanges() {
    if (this.modelArchitecture.architecture && this.modelArchitecture.architecture.length) {
      this.targetItems = this.modelArchitecture.architecture;
    }
  }

  ngOnInit() {
    if (this.selectedModel.modelGeneratedFrom !== 'Workflow') {
      this.getLayers();
    } else {
      this.sideBarGeneralItems.push(
        {
          'name': 'Model',
          'icon': 'mdi mdi-xml',
          'itemType': 'MODEL',
          'layerId': 'Model',
          'trainable': true
        });
      // adding model type key
      for (let item of this.sideBarGeneralItems) {
        item.modelType = 'Workflow';
      }
    }
  }

}
