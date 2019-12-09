import { Component, OnInit, ViewChild } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';
import { MatPaginator, MatTableDataSource, MatSort } from '@angular/material';
import { Router } from '@angular/router';


@Component({
  selector: 'app-data',
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.scss']
})
export class DataComponent implements OnInit {

  public listOfData: any = [];
  public selectedData: any = {};
  public automlFormData: any = {};
  public filterConfig: any = {};
  public filter: any = '';
  public dropzoneConfig: any = {
    openFileBrowser: false,
    url: ApiRoutes.data,
    acceptedFiles: `
          image/*,
          application/json,
          text/csv,
          application/csv,
          application/excel,
          application/vnd.ms-excel,
          application/vnd.msexcel,
          text/anytext,
          text/comma-separated-value,
          .csv,
          .json,
          .zip,
          application/zip,
          video/mp4,
          .mp4,
          .md,
          .txt`,
    acceptedFilesMsg: 'Allowed file types are : CSV, JSON, IMAGES (.PNG, .jpeg, .jpg, .webp), MP4 VIDEO, and .zip'
  };
  public editorOptions: any = {
    theme: 'vs-light',
    language: 'json'
  };

  public displayedColumns: string[] = [];
  public dataSource: MatTableDataSource<any[]>;

  public showFilterPanel = false;
  public uploadFiles = false;
  public isLoading = false;
  public isContentLoading = false;

  public tabSelectedIndex = 0;
  public uploadFilesCounter = 0;
  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;
  message = AlertMessages.DATA.deleteConfirmationData;
  public baseImageInfo: any = {};
  constructor(private apiService: HttpService, private utilService: UtilService, private router: Router) { }

  public changeSelectedIndex(index: number) {
    this.tabSelectedIndex = index;
  }

  public uploadFilesDone() {
    this.changeSelectedIndex(0);
    this.getAllData();
    this.uploadFiles = false;
    this.uploadFilesCounter = 0;
  }

  public uploadNewFiles() {

    if (this.tabSelectedIndex === 1) {
      this.dropzoneConfig.openFileBrowser = new Date();
    } else {
      this.dropzoneConfig.openFileBrowser = false;
      this.changeSelectedIndex(1);
      this.uploadFiles = true;
      this.selectedData = {};
    }

  }

  public newAutoML() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.dataAutoML(this.selectedData.id))
      .pipe(finalize(() => {
        this.isContentLoading = false;
        // this.mockAutoML();
      }))
      .subscribe(response => {
        this.changeSelectedIndex(2);
        this.automlFormData = response;
        this.automlFormData.selectedData = this.selectedData;
      });
  }

  public mockAutoML() {
    this.automlFormData = {
      'data': [{
        'position': 1,
        'variable': 'mpg',
        'dtype': 'float64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 2,
        'variable': 'cylinders',
        'dtype': 'int64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 3,
        'variable': 'displacement',
        'dtype': 'float64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 4,
        'variable': 'horsepower',
        'dtype': 'float64',
        'missing_val': 6,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 5,
        'variable': 'weight',
        'dtype': 'int64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 6,
        'variable': 'acceleration',
        'dtype': 'float64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 7,
        'variable': 'model year',
        'dtype': 'int64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 8,
        'variable': 'origin',
        'dtype': 'int64',
        'missing_val': 0,
        'changedataType': 'Continuous',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      },
      {
        'position': 9,
        'variable': 'car name',
        'dtype': 'object',
        'missing_val': 0,
        'changedataType': 'Categorical',
        'imputation_method': 'None',
        'data_transformation_step': 'None',
        'use_for_model': true
      }],
      'options': {
        'changedataTypes': [
          'None',
          'Continuous',
          'Categorical'
        ],
        'imputation_methods': [
          'None',
          'Mean',
          'Median',
          'Mode',
          'Back fill',
          'Forward fill'
        ],
        'data_transformation_steps': [
          'None',
          'One Hot Encoding',
          'Label Encoding',
          'Normalize',
          'Scaling Standard',
          'Scaling Min Max',
          'Scaling Max Absolute'
        ]
      },
      'idforData': 1533033362
    };
    this.automlFormData.selectedDataID = this.selectedData.id;
    this.changeSelectedIndex(2);
  }

  public getAllData(refresh = false) {
    this.isLoading = true;
    const options = {
      params: {
        refresh: refresh
      }
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.data, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.listOfData = response;
        // select first record by default
        if (response && response.length && !this.uploadFiles) {
          this.viewData(response[0]);
        } else if (!refresh) {
          this.uploadNewFiles();
        }
      }, err => {
        this.uploadNewFiles();
      });
  }

  public refresh() {
    this.getAllData(true);
  }

  public viewData(data: any) {
    this.selectedData = data;
    this.uploadFiles = false;
    this.uploadFilesCounter = 0;
    this.changeSelectedIndex(0);
  }

  public deleteData() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.dataGet(this.selectedData.id))
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.getAllData();
        this.utilService.alert(AlertMessages.DATA.delete);
      });
  }

  public updateName(name: any) {
    if (name.innerText === this.selectedData.id) {
      return;
    }
    this.isLoading = true;
    const options = {
      body: {
        newName: name.innerText
      }
    };
    this.apiService.request(ApiRoutes.methods.PUT, ApiRoutes.dataRename(this.selectedData.id), options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.selectedData.id = response.id;
        this.selectedData.name = response.name;
        this.selectedData.url = response.url;
        this.selectedData.filePath = response.filePath;
      }, errorResponse => {
        name.innerText = this.selectedData.id;
      });
  }

  public onDataUploadSuccess($event: any[]) {
    const uploadedData = ($event.length === 3) ? $event[1] : $event;
    this.uploadFilesCounter++;
    this.utilService.alert(`${this.uploadFilesCounter} ${AlertMessages.DATA.upload}`);
    this.listOfData = uploadedData.concat(this.listOfData);
  }

  public predictData(server: String) {
    this.showFilterPanel = true;
    this.filterConfig = {
      route: (server === 'ZMK') ? ApiRoutes.modelLoaded : ApiRoutes.modelDeployed,
      params: { server: server }
    };
  }

  public closeFilter() {
    this.showFilterPanel = false;
  }

  public predictNow(selectedModel: any) {
    this.showFilterPanel = false;
    this.isContentLoading = true;
    const options = {
      params: {
        dataId: this.selectedData.id,
        modelID: selectedModel.id,

      }
    };
    const api = (selectedModel.server === 'ZMK') ? ApiRoutes.predictData : ApiRoutes.scoreData;
    this.apiService.request(ApiRoutes.methods.GET, api, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.getAllData();
        this.utilService.alert(AlertMessages.DATA.predictionDone);
      });
  }

  public dowloadData() {
    this.isContentLoading = true;
    const options = {
      responseType: 'blob'
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.dataDownload(this.selectedData.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.utilService.saveFile(response, this.selectedData.name);
        this.utilService.alert(AlertMessages.DATA.download);
      });
  }

  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }

  public onFilteredItemSelection($event: any) {
    if ($event && $event.id) {
      this.predictNow($event);
    }
  }

  public uploadNewCumulocityData() {
    this.changeSelectedIndex(3);
  }

  public goToInfoTab() {
    this.changeSelectedIndex(0);
  }

  public previewData() {
    this.changeSelectedIndex(4);
    this.readDATA();
  }

  readDATA() {
    this.isContentLoading = true;
    this.displayedColumns = [];
    this.dataSource = new MatTableDataSource([]);
    this.selectedData.jsonCode = '';
    const options = {
      responseType: 'text'
    };
    this.apiService.request(ApiRoutes.methods.GET, window.location.origin + this.selectedData.url, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        if (this.selectedData.type === 'CSV') {
          const csvData = this.utilService.transformCSVDataToJson(response);
          this.displayedColumns = csvData.header;
          this.dataSource = new MatTableDataSource(csvData.data);
          this.dataSource.paginator = this.paginator;
          this.dataSource.sort = this.sort;
        }
        if (this.selectedData.type === 'JSON') {
          this.selectedData.jsonCode = response;
        }
      });
  }

  newWeldingData() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.dataBaseImageForWelding)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.baseImageInfo = response;
        this.changeSelectedIndex(5);
      }, errorResponse => {
        console.log(errorResponse);
      });
  }

  onWeldingConfigFormSubmit(data: any) {
    this.isContentLoading = true;
    let options = {
      body: data
    };
    let api = ApiRoutes.dataBaseImageForWelding;
    if (data.generateImages) {
      api = ApiRoutes.generateImageForWelding;
    }
    this.apiService.request(ApiRoutes.methods.POST, api, options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.baseImageInfo = response;
        this.changeSelectedIndex(5);
        if (data.generateImages) {
          this.router.navigate(['tasks']);
        }
      }, errorResponse => {
        console.log(errorResponse);
      });
  }

  ngOnInit() {
    this.getAllData();
  }

}
