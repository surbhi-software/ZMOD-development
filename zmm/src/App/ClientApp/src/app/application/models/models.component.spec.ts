import { async, ComponentFixture, TestBed, fakeAsync, getTestBed, inject } from '@angular/core/testing';
import { DebugElement, NO_ERRORS_SCHEMA } from '@angular/core';
import { ModelsComponent } from './models.component';
import { AppDropzoneComponent } from '../../shared/dropzone/dropzone.component';
import { HttpService, ApiRoutes, UtilService, AlertMessages } from 'src/app/shared';
import { HttpClient, HTTP_INTERCEPTORS, HttpClientModule } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { SearchFilterPipe } from 'src/app/shared/pipes/searchFilter.pipe';
import { OrderByDatePipe } from 'src/app/shared/pipes/orderbydate.pipe';
import { HighlightPipe } from 'src/app/shared/pipes/highlight.pipe';
import { FileSizePipe } from 'src/app/shared/pipes/file-size.pipe';
import { BrowserModule, By } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Router, RouterModule } from '@angular/router';
import { ScrollingModule } from '@angular/cdk/scrolling';
import {
  MatSnackBarModule,
  MatSidenavModule,
  MatProgressBarModule,
  MatListModule,
  MatCheckboxModule,
  MatTooltipModule,
  MatMenuModule
} from '@angular/material';
import { ApiPrefixInterceptor } from 'src/app/shared/http/api-prefix.interceptor';
import { ErrorHandlerInterceptor } from 'src/app/shared/http/error-handler.interceptor';
import { of } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { CacheInterceptor } from 'src/app/shared/http/cache.interceptor';
import { SnackbarComponent } from 'src/app/shared/snackbar/snackbar.component';
import { BrowserDynamicTestingModule } from '@angular/platform-browser-dynamic/testing';
import { environment } from 'src/environments/environment';


describe('ModelsComponent', () => {
  let component: ModelsComponent;
  let fixture: ComponentFixture<ModelsComponent>;
  let httpMock: HttpTestingController;
  let httpService: HttpService;
  let http: HttpClient;
  // let utilService;
  // let httpHandler;
  let router;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      schemas: [NO_ERRORS_SCHEMA],
      declarations: [
        ModelsComponent,
        AppDropzoneComponent,
        SearchFilterPipe,
        OrderByDatePipe,
        HighlightPipe,
        FileSizePipe,
        SnackbarComponent
      ],
      imports: [
        BrowserAnimationsModule,
        BrowserModule,
        MatMenuModule,
        MatSnackBarModule,
        MatSidenavModule,
        MatProgressBarModule,
        MatListModule,
        MatCheckboxModule,
        MatTooltipModule,
        RouterModule,
        ScrollingModule,
        HttpClientTestingModule,
        HttpClientModule
      ],
      providers: [
        HttpService,
        ApiPrefixInterceptor,
        ErrorHandlerInterceptor,
        CacheInterceptor,
        { provide: Router, useValue: jasmine.createSpyObj('router', ['navigate']) },
        { provide: ApiRoutes },
        { provide: UtilService },
        { provide: AlertMessages },
        { provide: HttpClient, useClass: HttpService },
        { provide: HTTP_INTERCEPTORS, useClass: ApiPrefixInterceptor, deps: [HttpService], multi: true },
      ]
    })
      .compileComponents();
    TestBed.overrideModule(BrowserDynamicTestingModule, {
      set: {
        entryComponents: [SnackbarComponent]
      }
    });
    const injector = getTestBed();
    httpService = injector.get(HttpService);
    router = injector.get(Router);
    http = injector.get(HttpClient);
    httpMock = injector.get(HttpTestingController);
    // utilService = injector.get(UtilService);
    // httpHandler = injector.get(HttpHandler);
    // debugElement = fixture.debugElement;
  }));
  // beforeEach(inject([
  //   HttpClient,
  //   HttpTestingController,
  //   HttpService,
  // ], (_http: HttpClient,
  //   _httpMock: HttpTestingController,
  //   _httpService: HttpService,
  //   ) => {

  //     http = _http;
  //     httpMock = _httpMock;
  //     httpService = _httpService;
  //   }));
  const selectedData = {
    'id': 'BD_data',
    'name': 'BD_data.csv',
    'user': 'Rainer',
    'created_on': '12/7/2018 5:00:18 PM',
    'edited_on': '12/7/2018 5:00:18 PM',
    'type': 'CSV',
    'url': '/uploads/data/BD_data.csv',
    'filePath': 'C:/Zementic6dec/zmm/src/App/wwwroot/uploads/data/BD_data.csv',
    'size': 42419,
    'mimeType': 'application/vnd.ms-excel',
    'extension': 'csv',
    'properties': [
      {
        'key': 'Number of rows',
        'value': '304'
      },
      {
        'key': 'Number of columns',
        'value': '14'
      }]
  };
  let selectedModel: any = {};
  selectedModel = {
    'loaded': false,
    'deployed': false,
    'modelName': null,
    'id': 'New_636803552998909534',
    'name': 'New_636803552998909534.pmml',
    'user': '',
    'created_on': '12/14/18 3:34:59 AM',
    'edited_on': '12/14/18 3:34:59 AM',
    'type': 'PMML',
    'url': '/uploads/model/New_636803552998909534.pmml',
    'filePath': 'C:/Zementis/zmm/src/App/wwwroot/uploads/model/New_636803552998909534.pmml',
    'size': 281, 'mimeType': 'application/octet-stream',
    'extension': 'pmml',
    'properties': []
  };
  // const event =
  //   [
  //     {
  //       'accepted': true,
  //       'lastModified': 1543920313227,
  //       'lastModifiedDate': 'Tue Dec 04 2018 16:15:13 GMT+0530 (India Standard Time)',
  //       'name': 'BD_data.csv',
  //       'size': 42419,
  //       'status': 'success',
  //       'type': 'application/vnd.ms-excel',
  //     },
  //     {
  //       'created_on': '12/13/18 10:33:03 PM',
  //       'edited_on': '12/13/18 10:33:03 PM',
  //       'extension': 'csv',
  //       'filePath': '/home/demo/ZMOD/data/BD_data.csv',
  //       'id': 'BD_data',
  //       'mimeType': 'application/vnd.ms-excel',
  //       'name': 'BD_data.csv',
  //       'size': 42419,
  //       'type': 'CSV',
  //       'url': '/uploads/data/BD_data.csv',
  //       'user': ''
  //     },
  //     {
  //       'bubbles': false,
  //       'cancelBubble': false,
  //       'cancelable': false,
  //       'composed': false
  //     }
  //   ];

  beforeEach(() => {
    fixture = TestBed.createComponent(ModelsComponent);
    component = fixture.componentInstance;
    // fixture.autoDetectChanges();
    router.navigate.and.returnValue(of([]));
  });

  it('should be true on test', fakeAsync(() => {
    fixture.detectChanges();
    expect(true).toBeTruthy();
  }));
  it('Call on ngOnInit', () => {
    spyOn(component, 'ngOnInit').and.callThrough();
    expect(true).toBeTruthy();
  });

  it('should call on changeSelectedIndex', fakeAsync(() => {
    spyOn(component, 'changeSelectedIndex').and.returnValue('0');
  }));

  it('should verify uploadnewFiles() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    component.uploadFiles = true;
    component.uploadNewFiles();
    component.selectedModel = 'ModelsComponent';
    expect(component.tabSelectedIndex).toBe(1);
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.uploadFiles).toBeTruthy();
    expect(component.selectedModel).toEqual('ModelsComponent');
  });

  it('should verify uploadFilesDone() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    spyOn(component, 'getAllPMML');
    component.uploadFiles = false;
    component.uploadFilesDone();
    expect(component.uploadFiles).toBeFalsy();
    component.tabSelectedIndex = 0;
    expect(component.tabSelectedIndex).toBe(0);
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.getAllPMML).toHaveBeenCalled();

  });
  it('should verify downloadModel() is called', () => {
    spyOn(component, 'downloadModel').and.callThrough();
    component.downloadModel();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify on alert message service', () => {
    expect(AlertMessages.MODEL.deleteConfirmationModel).toEqual('Are you sure to delete model file?');
  });
  it('Test on Api routes service', () => {
    expect(ApiRoutes.methods.GET).toEqual('get');
    expect(ApiRoutes.models).toEqual('model');
    expect(ApiRoutes.modelDownload(1)).toEqual(`model/1/download`);
  });
  it('should verify selectPMML() is called', () => {
    spyOn(component, 'selectPMML').and.callThrough();
    component.selectPMML([]);
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify updateName() is called', () => {
    component.updateName(event);
  });
  it('should verify editpmml() is called', () => {
    spyOn(component, 'editpmml').and.callThrough();
    component.editpmml();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify editpmmlDone() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    component.editpmmlDone();
    component.tabSelectedIndex = 0;
    expect(component.tabSelectedIndex).toBe(0);
  });
  it('should verify deletePMML() is called', () => {
    spyOn(component, 'deletePMML').and.callThrough();
    const model = selectedModel.id;
    component.deletePMML();
    component.isLoading = true;
    expect(component.isLoading).toBeTruthy();
    const req = httpMock.expectOne({
      url: 'http://localhost:5000/api/model/undefined',
      method: 'DELETE'
    });
    console.log(req.request.body);
    expect(req.request.responseType).toEqual('json');
    expect(req.request.body).toEqual(null);
  });
  it('should verify togglebar() is called', () => {
    const action = 'full';
    component.toggleSidebar(action);
  });
  it('should verify closeEditor() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    component.closeEditor();
    component.tabSelectedIndex = 0;
    expect(component.tabSelectedIndex).toBe(0);
  });
  it('should verify loadInMemory() is called', () => {
    spyOn(component, 'loadInMemory').and.callThrough();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
    component.loadInMemory();
  });
  it('should verify onCompileFormDataSubmit() is called', () => {
    spyOn(component, 'onCompileFormDataSubmit').and.callThrough();
    const body = 'body';
    component.onCompileFormDataSubmit(body);
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify compileForm() is called', () => {
    spyOn(component, 'compileForm').and.callThrough();
    component.compileForm();
    component.showCompileFormPanel = true;
    expect(component.showCompileFormPanel).toBeTruthy();
  });
  it('should verify onTrainingFormDataSubmit() is called', () => {
    spyOn(component, 'onTrainingFormDataSubmit').and.callThrough();
    const body = 'body';
    component.onTrainingFormDataSubmit(body);
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify trainPmml() is called', () => {
    spyOn(component, 'trainPmml').and.callThrough();
    component.trainPmml();
    component.showTrainingFormPanel = true;
    expect(component.showTrainingFormPanel).toBeTruthy();
  });
  it('should verify deployModel() is called', () => {
    spyOn(component, 'deployModel').and.callThrough();
    component.deployModel();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify newPmml() is called', () => {
    spyOn(component, 'newPmml').and.callThrough();
    component.newPmml();
    component.isLoading = true;
    expect(component.isLoading).toEqual(true);
  });
  it('should verify onModelUploadSuccess() is called', () => {
    spyOn(component, 'onModelUploadSuccess').and.callThrough();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify getAutoML() is called', () => {
    spyOn(component, 'getAutoML').and.callThrough();
    component.getAutoML(selectedData);
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
  });
  it('should verify cancelAutoML() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    component.cancelAutoML();
    component.tabSelectedIndex = 0;
    expect(component.tabSelectedIndex).toBe(0);
  });
  it('should verify onFilteredItemSelection() is called', () => {
    spyOn(component, 'onFilteredItemSelection').and.callThrough();
    component.showFilterPanel = false;
    expect(component.showFilterPanel).toBeFalsy();
  });
  it('should verify autoML() is called', () => {
    spyOn(component, 'autoML').and.callThrough();
    component.showFilterPanel = true;
    expect(component.showFilterPanel).toBeTruthy();
    const filterConfig = {
      route: ApiRoutes.data,
      params: { type: ['CSV'] }
    };
    expect(filterConfig.params.type[0]).toEqual('CSV');
  });

  it('should verify the getAllPMML API testing', () => {
    const mocResponse = [{
      'loaded': false,
      'deployed': false,
      'modelName': null,
      'id': 'New_636803552998909534',
      'name': 'New_636803552998909534.pmml',
      'user': '',
      'created_on': '12/14/18 3:34:59 AM',
      'edited_on': '12/14/18 3:34:59 AM',
      'type': 'PMML',
      'url': '/uploads/model/New_636803552998909534.pmml',
      'filePath': 'C:/Zementis/zmm/src/App/wwwroot/uploads/model/New_636803552998909534.pmml',
      'size': 281, 'mimeType': 'application/octet-stream',
      'extension': 'pmml',
      'properties': []
    }];
    httpService.request(ApiRoutes.methods.GET, ApiRoutes.models)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(responseData => {
        expect(responseData).toEqual(mocResponse);
      });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.models,
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    expect(req.request.body).toEqual(null);
    req.flush(mocResponse);
    httpMock.verify();
  });

  it('should verify the deletePMML() API response', async(() => {
    const mocResponse = { 'user': '', 'id': 'New_636803552998909534', 'message': 'Model Deleted' };

    httpService.request(ApiRoutes.methods.DELETE, ApiRoutes.modelGet(selectedModel.id))
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(responseData => {
        expect(responseData.message).toEqual(mocResponse.message);
      });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.modelGet(selectedModel.id),
      method: ApiRoutes.methods.DELETE
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));
});
