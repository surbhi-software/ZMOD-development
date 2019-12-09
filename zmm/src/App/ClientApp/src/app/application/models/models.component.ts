import { Component, OnInit } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';
import { Router } from '@angular/router';

@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrls: ['./models.component.scss']
})
export class ModelsComponent implements OnInit {

  public listOfModels: any = [];
  public selectedModel: any = {};
  public selectedModelArchitecture: any = {};
  public isLoading = false;
  public uploadFiles = false;
  public showFilterPanel = false;
  public showTrainingFormPanel = false;
  public showCompileFormPanel = false;
  public showCompileError = false;
  public automlFormData: any;
  public isContentLoading = false;
  public filterConfig: any = {};
  public showUploadButton = true;
  public listOfZMKInstances = [];
  message = AlertMessages.MODEL.deleteConfirmationModel;
  public filter: any = '';
  public publishModelData = false;
  public publishModelDataList: any = [{ "loaded": false, "deployed": false, "modelName": null, "dateCreated": "2019-06-26T09:25:23", "id": "cancer_svc", "name": "cancer_svc.pmml", "user": "", "created_on": "6/26/19 9:25:23 AM", "edited_on": "6/26/19 9:25:23 AM", "type": "PMML", "url": "/model/cancer_svc.pmml", "filePath": "/home/ubuntu/Repos/ZMOD/Models/cancer_svc.pmml", "size": 137519, "mimeType": "application/octet-stream", "extension": "pmml", "properties": [] }, { "loaded": false, "deployed": false, "modelName": null, "dateCreated": "2019-06-26T04:51:03", "id": "adms", "name": "adms.pmml", "user": "", "created_on": "6/26/19 4:51:03 AM", "edited_on": "6/26/19 4:51:03 AM", "type": "PMML", "url": "/model/adms.pmml", "filePath": "/home/ubuntu/Repos/ZMOD/Models/adms.pmml", "size": 2638, "mimeType": "application/octet-stream", "extension": "pmml", "properties": [] }, { "loaded": false, "deployed": false, "modelName": null, "dateCreated": "2019-06-26T04:44:59", "id": "New_636971210439769208", "name": "New_636971210439769208.pmml", "user": "", "created_on": "6/26/19 4:44:59 AM", "edited_on": "6/26/19 4:44:59 AM", "type": "PMML", "url": "/model/New_636971210439769208.pmml", "filePath": "/home/ubuntu/Repos/ZMOD/Models/New_636971210439769208.pmml", "size": 22794912, "mimeType": "application/octet-stream", "extension": "pmml", "properties": [] }, { "loaded": false, "deployed": false, "modelName": null, "dateCreated": "2019-06-26T04:41:51", "id": "Distracted_Driver_PP", "name": "Distracted_Driver_PP.pmml", "user": "", "created_on": "6/26/19 4:41:51 AM", "edited_on": "6/26/19 4:41:51 AM", "type": "PMML", "url": "/model/Distracted_Driver_PP.pmml", "filePath": "/home/ubuntu/Repos/ZMOD/Models/Distracted_Driver_PP.pmml", "size": 22785366, "mimeType": "application/octet-stream", "extension": "pmml", "properties": [] }, { "dateCreated": "2019-07-01T09:31:30.9773017+00:00", "id": "Predicted_admissions", "name": "Predicted_admissions.csv", "user": "", "created_on": "7/1/19 9:31:30 AM", "edited_on": "7/1/19 9:31:30 AM", "type": "CSV", "url": "/api/data/preview/Predicted_admissions.csv", "filePath": "/home/ubuntu/Repos/ZMOD/Data/Predicted_admissions.csv", "size": 20518, "mimeType": "application/json", "extension": "csv", "properties": [] }, { "dateCreated": "2019-06-26T04:45:16.5572998+00:00", "id": "New_636971210439769208", "name": "New_636971210439769208", "user": null, "created_on": "6/26/19 4:45:16 AM", "edited_on": "6/26/19 4:45:16 AM", "type": "FOLDER", "url": null, "filePath": "/home/ubuntu/Repos/ZMOD/Data/New_636971210439769208", "size": 0, "mimeType": "", "extension": "", "properties": [{ "key": "Subdirectories", "value": "0" }, { "key": "Files", "value": "0" }] }, { "dateCreated": "2019-06-26T04:43:20.7856626+00:00", "id": "admissions_test", "name": "admissions_test.csv", "user": "", "created_on": "6/26/19 4:43:20 AM", "edited_on": "6/26/19 4:43:20 AM", "type": "CSV", "url": "/api/data/preview/admissions_test.csv", "filePath": "/home/ubuntu/Repos/ZMOD/Data/admissions_test.csv", "size": 15897, "mimeType": "text/csv", "extension": "csv", "properties": [{ "key": "Number of Rows", "value": "645" }, { "key": "Number of Columns", "value": "2" }] }, { "dateCreated": "2019-06-26T04:43:20.7336627+00:00", "id": "admissions", "name": "admissions.csv", "user": "", "created_on": "6/26/19 4:43:20 AM", "edited_on": "6/26/19 4:43:20 AM", "type": "CSV", "url": "/api/data/preview/admissions.csv", "filePath": "/home/ubuntu/Repos/ZMOD/Data/admissions.csv", "size": 17192, "mimeType": "text/csv", "extension": "csv", "properties": [{ "key": "Number of Rows", "value": "645" }, { "key": "Number of Columns", "value": "3" }] }, { "dateCreated": "2019-06-26T04:42:10.7898819+00:00", "id": "img_100004", "name": "img_100004.jpg", "user": "", "created_on": "6/26/19 4:42:10 AM", "edited_on": "6/26/19 4:42:10 AM", "type": "IMAGE", "url": "/api/data/preview/img_100004.jpg", "filePath": "/home/ubuntu/Repos/ZMOD/Data/img_100004.jpg", "size": 37891, "mimeType": "image/jpg", "extension": "jpg", "properties": [{ "key": "Width", "value": "640 px" }, { "key": "Height", "value": "480 px" }] }, { "dateCreated": "2019-06-26T04:42:10.7898819+00:00", "id": "img_100009", "name": "img_100009.jpg", "user": "", "created_on": "6/26/19 4:42:10 AM", "edited_on": "6/26/19 4:42:10 AM", "type": "IMAGE", "url": "/api/data/preview/img_100009.jpg", "filePath": "/home/ubuntu/Repos/ZMOD/Data/img_100009.jpg", "size": 42355, "mimeType": "image/jpg", "extension": "jpg", "properties": [{ "key": "Width", "value": "640 px" }, { "key": "Height", "value": "480 px" }] }, { "dateCreated": "2019-06-26T04:41:32.3300024+00:00", "id": "DisDriver", "name": "DisDriver", "user": null, "created_on": "6/26/19 4:41:32 AM", "edited_on": "6/26/19 4:41:32 AM", "type": "FOLDER", "url": null, "filePath": "/home/ubuntu/Repos/ZMOD/Data/DisDriver", "size": 0, "mimeType": "", "extension": "", "properties": [{ "key": "Subdirectories", "value": "22" }, { "key": "Files", "value": "3324" }] }];;
  constructor(private apiService: HttpService, private utilService: UtilService, private router: Router) { }

  public dropzoneConfig: any = {
    openFileBrowser: false,
    url: ApiRoutes.models,
    acceptedFiles: `
    .pmml,
    .onyx
    `,
    acceptedFilesMsg: 'Allowed file type are PMML, ONYX'
  };
  public tabSelectedIndex = 0;

  public changeSelectedIndex(index: number) {
    this.tabSelectedIndex = index;
  }

  public tabSelectedIndexChanged($event: any) {
  }

  public uploadNewFiles() {
    if (this.tabSelectedIndex === 1) {
      this.dropzoneConfig.openFileBrowser = new Date();
    } else {
      this.dropzoneConfig.openFileBrowser = false;
      this.changeSelectedIndex(1);
      this.uploadFiles = true;
      this.selectedModel = {};
    }
  }

  public uploadFilesDone() {
    this.changeSelectedIndex(0);
    this.getAllPMML();
    this.uploadFiles = false;
  }



  public downloadModel() {
    this.isContentLoading = true;
    const options = {
      responseType: 'blob'
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelDownload(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.utilService.saveFile(response, this.selectedModel.name);
        this.utilService.alert(AlertMessages.MODEL.download);
      });

  }

  public getAllPMML(refresh = false) {
    this.isLoading = true;
    const options = {
      params: {
        refresh: refresh
      }
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.models, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(responseData => {
        this.listOfModels = responseData;
        // select first record by default
        if (this.listOfModels && this.listOfModels.length && !this.uploadFiles) {
          this.selectPMML(this.listOfModels[0]);
        } else if (!refresh) {
          this.uploadNewFiles();
        }
      }, err => {
        this.uploadNewFiles();
      });
  }

  public refresh() {
    this.getAllPMML(true);
  }

  public selectPMML(selectedModel: any) {
    this.isContentLoading = true;
    this.selectedModel = selectedModel;
    this.changeSelectedIndex(0);
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelGet(selectedModel.id))
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.selectedModel = responseData;
      });
  }

  public updateName(name: any) {
    if (name.innerText === this.selectedModel.id) {
      return;
    }
    this.isLoading = true;
    const options = {
      body: {
        newName: name.innerText
      }
    };
    this.apiService.request(ApiRoutes.methods.PUT, ApiRoutes.modelRename(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.selectedModel.id = response.id;
        this.selectedModel.name = response.name;
        this.selectedModel.url = response.url;
        this.selectedModel.filePath = response.filePath;
        console.log(this.selectedModel.id, response.id);
      }, errorResponse => {
        name.innerText = this.selectedModel.id;
      });
  }

  public editpmml() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelEdit(this.selectedModel.id))
      .pipe(finalize(() => { this.isContentLoading = false; this.changeSelectedIndex(2); }))
      .subscribe(responseData => {
        this.selectedModelArchitecture = responseData;
        this.changeSelectedIndex(2);
      });
  }

  public editpmmlDone() {
    this.changeSelectedIndex(0);
  }

  public deletePMML() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.modelGet(this.selectedModel.id))
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(responseData => {
        this.getAllPMML();
        this.utilService.alert(AlertMessages.MODEL.delete);
      });
  }

  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }

  public closeEditor() {
    this.changeSelectedIndex(0);
    this.selectPMML(this.selectedModel);
  }
  public getZMKInstances() {
    this.isLoading = true;
    const options = {
      params: {
        type: 'ZMK'
      }
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.instance, options)
      .pipe(finalize(() => {
        this.isLoading = false;
      }))
      .subscribe(response => {
        this.listOfZMKInstances = response;
      });
  }
  public loadInMemory(zmkID: any) {
    this.isContentLoading = true;
    const options = {
      params: {
        instanceId: zmkID
      }
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelLoad(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.selectedModel.loaded = responseData.loaded;
        this.utilService.alert(AlertMessages.MODEL.load);
      });
  }

  public unloadFromMemory() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.modelUnload(this.selectedModel.id))
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.selectedModel.loaded = responseData.loaded;
        this.utilService.alert(AlertMessages.MODEL.unload);
      });
  }

  public onCompileFormDataSubmit(body: any) {
    this.isContentLoading = true;
    const options = {
      body: body
    };
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.modelCompile(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.utilService.alert(AlertMessages.MODEL.compile);
      }, err => {
        this.showCompileError = true;
        this.utilService.alert(AlertMessages.MODEL.err);

      });
  }

  public compileForm() {
    this.showCompileFormPanel = true;
  }

  public onTrainingFormDataSubmit(body: any) {
    this.isContentLoading = true;
    const options = {
      body: body
    };
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.modelTrain(this.selectedModel.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.utilService.alert(AlertMessages.MODEL.train);
        this.router.navigate(['tasks']);
      });
  }

  public trainPmml() {
    this.showTrainingFormPanel = true;
  }

  public deployModel() {
    this.isContentLoading = true;
    const modelDeployEndPoint = ApiRoutes.modelDeploy(this.selectedModel.id);
    const route = this.selectedModel.deployed ? ApiRoutes.modelDeployUndo(this.selectedModel.id) : modelDeployEndPoint;
    this.apiService.request(ApiRoutes.methods.GET, route)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.selectedModel.deployed = responseData.deployed;
        this.utilService.alert(this.selectedModel.deployed ? AlertMessages.MODEL.deploy : AlertMessages.MODEL.deployUndo);
      });
  }

  public newPmml(type: string) {
    this.isLoading = true;
    this.uploadFiles = false;
    const options = {
      body: {
        type: type
      }
    };
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.modelCreate, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(responseData => {
        this.utilService.alert(responseData.name + AlertMessages.MODEL.create);
        this.getAllPMML();
      });
  }

  public onModelUploadSuccess($event: any[]) {
    this.listOfModels = $event[1].concat(this.listOfModels);
  }

  public getAutoML(selectedData: any) {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.dataAutoML(selectedData.id))
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(responseData => {
        this.changeSelectedIndex(3);
        this.automlFormData = responseData;
        this.automlFormData.selectedData = selectedData;
      });
  }

  public cancelAutoML() {
    this.changeSelectedIndex(0);
  }

  onFilteredItemSelection($event: any) {
    if ($event && $event.id) {
      this.getAutoML($event);
      this.showFilterPanel = false;
    }
  }

  public autoML() {
    this.showFilterPanel = true;
    this.filterConfig = {
      route: ApiRoutes.data,
      params: {
        type: ['CSV']
      }
    };
  }
  publishModel() {
    console.log('Publish model logic here');
    this.publishModelData = true;
  }
  closeFilter() {
    this.publishModelData = false;
  }

  ngOnInit() {
    this.getAllPMML();
    this.getZMKInstances();
  }

}
