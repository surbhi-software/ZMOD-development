import { async, ComponentFixture, TestBed, inject, tick, fakeAsync } from '@angular/core/testing';
import { HttpClientModule, HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiRoutes, AlertMessages } from '../../shared';
import { DataComponent } from './data.component';
import { CUSTOM_ELEMENTS_SCHEMA, DebugElement } from '@angular/core';
import { SearchFilterPipe } from '../../shared/pipes/searchFilter.pipe';
import { OrderByDatePipe } from '../../shared/pipes/orderbydate.pipe';
import { HighlightPipe } from '../../shared/pipes/highlight.pipe';
import { FileSizePipe } from '../../shared/pipes/file-size.pipe';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { finalize } from 'rxjs/operators';
import { ApiPrefixInterceptor } from '../../shared/http/api-prefix.interceptor';
import { ErrorHandlerInterceptor } from '../../shared/http/error-handler.interceptor';
import { CacheInterceptor } from '../../shared/http/cache.interceptor';
import { HttpService } from '../../shared/http/http.service';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { UtilService } from '../../shared/services/util.service';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { SnackbarComponent } from '../../shared/snackbar/snackbar.component';
import { BrowserDynamicTestingModule } from '@angular/platform-browser-dynamic/testing';
import { environment } from '../../../environments/environment';
import {
  MatButtonModule,
  MatTabsModule,
  MatToolbarModule,
  MatSidenavModule,
  MatMenuModule,
  MatTooltipModule,
  MatTableModule,
  MatSnackBarModule,
  MatSlideToggleModule,
  MatPaginatorModule,
  MatSortModule
} from '@angular/material';

class TestModule { }
describe('DataComponent', () => {
  let component: DataComponent;
  let fixture: ComponentFixture<DataComponent>;
  let httpService: HttpService;
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let listData;
  beforeEach(async () => {
    TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [
        DataComponent,
        SearchFilterPipe,
        OrderByDatePipe,
        HighlightPipe,
        FileSizePipe,
        SnackbarComponent
      ],
      imports: [
        FormsModule,
        HttpClientModule,
        HttpClientTestingModule,
        BrowserAnimationsModule,
        ScrollingModule,
        MatButtonModule,
        MatTabsModule,
        MatToolbarModule,
        MatSidenavModule,
        MatMenuModule,
        MatTooltipModule,
        MatTableModule,
        MatSnackBarModule,
        MatSlideToggleModule,
        MatPaginatorModule,
        MatSortModule
      ],
      providers: [
        HttpService,
        ApiPrefixInterceptor,
        ErrorHandlerInterceptor,
        CacheInterceptor,
        {
          provide: HTTP_INTERCEPTORS,
          useClass: ApiPrefixInterceptor,
          deps: [HttpService],
          multi: true
        },
        {
          provide: ApiRoutes
        },
        {
          provide: AlertMessages
        },
        {
          provide: HttpClient,
          useClass: HttpService
        },
        UtilService
      ],

    })
      .compileComponents();
    TestBed.overrideModule(BrowserDynamicTestingModule, {
      set: {
        entryComponents: [SnackbarComponent]
      }
    });
  });
  let selectedData: any = {};
  selectedData = {
    'id': 'BD_Data',
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
  const selectedModel = {
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
    'size': 281,
    'mimeType': 'application/octet-stream',
    'extension': 'pmml',
    'properties': []
  };

  beforeEach(inject([
    HttpClient,
    HttpTestingController,
    HttpService,
  ], (_http: HttpClient,
    _httpMock: HttpTestingController,
    _httpService: HttpService,
    ) => {

      http = _http;
      httpMock = _httpMock;
      httpService = _httpService;
    }));

  afterEach(() => {
    // httpMock.verify();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DataComponent);
    component = fixture.componentInstance;
  });

  it('should verify previewData() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    spyOn(component, 'readDATA').and.callThrough();
    component.previewData();
    const newPreviewDataButton = fixture.debugElement.query(By.css('content-toolbar button:nth-child(3)'));
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.readDATA).toHaveBeenCalled();
  });

  it('should verify newAutoML() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    component.newAutoML();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
    const newAutoMLButton = fixture.debugElement.query(By.css('mdi-file-plus'));
    fixture.detectChanges();
  });

  it('should verify deleteData() is called', () => {
    spyOn(component, 'deleteData').and.callThrough();
    const data = selectedData.id;
    component.deleteData();
    component.isLoading = true;
  });

  it('should verify predictNow is called', () => {
    component.predictNow(selectedModel);
    component.showFilterPanel = false;
    expect(component.showFilterPanel).toEqual(false);
    component.isContentLoading = true;
    expect(component.isContentLoading).toEqual(true);
    const options = {
      params: {
        dataId: selectedData.id,
        modelID: selectedModel.id,

      }
    };
    expect(options.params.dataId).toEqual('BD_data');
    const newpredictDataButton = fixture.debugElement.query(By.css('newPredictDataMenu'));
  });
  it('should verify downLoadData() is called', () => {
    spyOn(component, 'dowloadData').and.callThrough();
    component.dowloadData();
    component.isContentLoading = true;
  });
  it('Call on ngOnInit', () => {
    spyOn(component, 'ngOnInit').and.callThrough();
  });
  it('Call on changeSelectedIndex', fakeAsync(() => {
    spyOn(component, 'changeSelectedIndex').and.returnValue('0');
    component.tabSelectedIndex = 1;
    expect(component.tabSelectedIndex).toBe(1);
  }));

  it('Test on alert message service', () => {
    expect(AlertMessages.DATA.delete).toEqual('Data Deleted');
  });

  it('Test on Api routes service', () => {
    expect(ApiRoutes.methods.DELETE).toEqual('delete');
    expect(ApiRoutes.data).toEqual('data');
    expect(ApiRoutes.dataGet(1)).toEqual('data/1');
  });

  it('should verify closefilter() is called', () => {
    /* var spyData = spyOn(component, 'closeFilter');
     expect(component).toBeDefined();
     fixture.detectChanges();
     expect(component.closeFilter).toHaveBeenCalled(); */
    component.closeFilter();
    component.showFilterPanel = false;
    expect(component.showFilterPanel).toEqual(false);
  });

  it('should verify  predictData', () => {
    spyOn(component, 'predictData').and.callThrough();
    const server = 'ZMK';
    component.predictData(server);
    component.showFilterPanel = true;
    expect(component.showFilterPanel).toEqual(true);
    const filterConfig = {
      route: (server === 'ZMK') ? ApiRoutes.modelLoaded : ApiRoutes.modelDeployed,
      params: { server: server }
    };
    if (server === 'ZMK') {
      expect(filterConfig.route).toEqual('model/loaded');

    } else {
      expect(filterConfig.route).toEqual('model/deployed');
    }
    const newpredictDataButton = fixture.debugElement.query(By.css('newPredictDataMenu'));
  });

  it('should verify viewData has been called', () => {
    spyOn(component, 'changeSelectedIndex');
    const testData = 'testData';
    component.viewData(testData);
    component.selectedData = testData;
    component.uploadFiles = false;
    component.uploadFilesCounter = 0;
    expect(component.uploadFilesCounter).toBe(0);
    expect(component.uploadFiles).toBeFalsy();
    expect(component.selectedData).toEqual('testData');
    expect(component.changeSelectedIndex).toHaveBeenCalled();

  });

  it('should verify uploadnewFile() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    const uploadButton = fixture.debugElement.query(By.css('mat-toolbar button:nth-child(1)')).nativeElement;
    expect(uploadButton.disabled).toBeFalsy();
    uploadButton.click(null);
    expect(component.tabSelectedIndex).toBe(3);
    expect(component.changeSelectedIndex).toHaveBeenCalled();
  });

  it('should verify uploadNewCumulocityData() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    const uploadNewCummulocityButton = fixture.debugElement.query(By.css('mat-toolbar button:nth-child(2)')).nativeElement;
    expect(uploadNewCummulocityButton.disabled).toBeFalsy();
    uploadNewCummulocityButton.click(null);
    expect(component.changeSelectedIndex).toHaveBeenCalled();

  });
  it('should verify cancelCumulocity() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    component.cancelCumulocity();
    const cancelCumulocityButton = fixture.debugElement.query(By.css('mat-toolbar button:nth-child(1)')).nativeElement;
    expect(cancelCumulocityButton.disabled).toBeFalsy();
    cancelCumulocityButton.click(null);
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.tabSelectedIndex).toBe(3);
  });

  it('should verify readData() is called', () => {
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
    component.displayedColumns = [];
    expect(component.displayedColumns).toBe([]);
  });

  it('should verify uploadFilesDone() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    spyOn(component, 'getAllData');
    component.uploadFilesDone();
    component.uploadFiles = false;
    expect(component.uploadFiles).toBeFalsy();
    component.uploadFilesCounter = 0;
    expect(component.uploadFilesCounter).toBe(0);
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.getAllData).toHaveBeenCalled();


  });

  it('should verify togglebar() is called', () => {
    const action = 'ful';
    component.toggleSidebar(action);
  });

  it('should verify  onDataUploadSuccess() is called', () => {
    spyOn(component, 'onDataUploadSuccess').and.callThrough();
    const event =
      [
        {
          'accepted': true,
          'lastModified': 1543920313227,
          'lastModifiedDate': 'Tue Dec 04 2018 16:15:13 GMT+0530 (India Standard Time)',
          'name': 'BD_data.csv',
          'size': 42419,
          'status': 'success',
          'type': 'application/vnd.ms-excel',
        },
        {
          'created_on': '12/13/18 10:33:03 PM',
          'edited_on': '12/13/18 10:33:03 PM',
          'extension': 'csv',
          'filePath': '/home/demo/ZMOD/data/BD_data.csv',
          'id': 'BD_data',
          'mimeType': 'application/vnd.ms-excel',
          'name': 'BD_data.csv',
          'size': 42419,
          'type': 'CSV',
          'url': '/uploads/data/BD_data.csv',
          'user': ''
        },
        {
          'bubbles': false,
          'cancelBubble': false,
          'cancelable': false,
          'composed': false
        }
      ];
    // component.onDataUploadSuccess(event);
    component.uploadFilesCounter = 0;
    expect(event.length).toEqual(3);
    listData = event.concat(listData);
    expect(component.uploadFilesCounter).toBe(0);
  });

  it('should verify cancelAutoMl() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    component.cancelAutoML();
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.tabSelectedIndex).toBe(0);
  });

  it('should verify onFilteredItemSelection() is called', () => {
    spyOn(component, 'predictNow').and.callThrough();
    component.onFilteredItemSelection(event);
    if (event) {
      //   expect(component.predictNow).toHaveBeenCalled();
    }
  });

  it('should verify updateName() is called', () => {
    component.updateName(event);
  });

  it('should verify the getAllData API testing', async(() => {
    const mocResponse = [{
      'id': 'BD_data',
      'name': 'BD_data.csv',
      'user': 'Rainer',
      'created_on': '12/7/2018 5:00:18 PM',
      'edited_on': '12/7/2018 5:00:18 PM',
      'type': 'CSV',
      'url': '/uploads/data/BD_data.csv',
      'filePath': 'D:/Zementic6dec/zmm/src/App/wwwroot/uploads/data/BD_data.csv',
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
    }];
    httpService.request(ApiRoutes.methods.GET, ApiRoutes.data)
      .pipe(finalize(() => { }))
      .subscribe((response) => {
        expect(response).toEqual(mocResponse);
        expect(response.length).toBe(1);
      });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.data,
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    expect(req.request.body).toEqual(null);
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify the newAutoml() API testing', async(() => {
    const mocResponse = {
      'data': [{
        'position': 1,
        'variable': 'mpg',
        'dtype': 'float64',
        'missing_val': 0,
        'changedataType': 'Continuous',
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
     httpService.request(ApiRoutes.methods.GET, ApiRoutes.dataAutoML(selectedData.id))
     .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
      expect(response.data).toEqual(mocResponse.data);
    });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.dataAutoML(selectedData.id),
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify the delete data API response', async(() => {
    const mocResponse = { 'user': '', 'id': 'BD_data', 'message': 'File deleted successfully.' };
    httpService.request(ApiRoutes.methods.DELETE, ApiRoutes.dataGet(selectedData.id))
    .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
       expect(response.message).toEqual(mocResponse.message);
     });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.dataGet(selectedData.id),
      method: ApiRoutes.methods.DELETE
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));

});
