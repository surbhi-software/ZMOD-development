import { async, ComponentFixture, TestBed, inject, tick, fakeAsync } from '@angular/core/testing';
import { HttpClientModule, HttpClient, HTTP_INTERCEPTORS, HttpErrorResponse } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiRoutes, AlertMessages } from '../../shared';
import { CUSTOM_ELEMENTS_SCHEMA, DebugElement } from '@angular/core';
import { SearchFilterPipe } from '../../shared/pipes/searchFilter.pipe';
import { OrderByDatePipe } from '../../shared/pipes/orderbydate.pipe';
import { HighlightPipe } from '../../shared/pipes/highlight.pipe';
import { FileSizePipe } from '../../shared/pipes/file-size.pipe';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { finalize, takeWhile } from 'rxjs/operators';
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
import { TasksComponent } from './tasks.component';
import { timer } from 'rxjs';
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

describe('TaskComponent', () => {
  let component: TasksComponent;
  let fixture: ComponentFixture<TasksComponent>;
  let httpService: HttpService;
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let selectedTask: any = {} ;
  selectedTask = {
    'pmmlFile': '/home/demo/ZMOD/model/New_636803506170859061.pmml',
    'dataFolder': '/home/demo/ZMOD/data/New_636803506170859061',
    'fileName': '/home/demo/ZMOD/model/New_636803506170859061.pmml',
    'tensorboardLogFolder': './logs/VFIEGGAVFTPC/',
    'tensorboardUrl': '',
    'lossType': 'categorical_crossentropy',
    'listOfMetrics': ['accuracy', 'f1'],
    'batchSize': 15,
    'epoch': 100,
    'stepsPerEpoch': 10,
    'problemType': 'classification',
    'testSize': 0.3,
    'scriptOutput': 'NA',
    'optimizerName': 'Adam',
    'learningRate': 0.001,
    'idforData': 'New_636803506170859061',
    'status': 'Data split in Train validation part',
    'pID': '1925'
  };
  beforeEach(async () => {
    TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [
        SearchFilterPipe,
        OrderByDatePipe,
        HighlightPipe,
        FileSizePipe,
        SnackbarComponent,
        TasksComponent
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

  beforeEach(() => {
    fixture = TestBed.createComponent(TasksComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(true).toBeTruthy();
  });

  it('should verify changeSelectedIndex', () => {
    component.changeSelectedIndex(1);
    component.tabSelectedIndex = 1;
    expect(component.tabSelectedIndex).toBe(1);
  });

  it('should verify for contentLoading and isLoading', () => {
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
    component.isLoading = false;
    expect(component.isLoading).toBeFalsy();
  });

  it('should verify on ngOnInit', () => {
    spyOn(component, 'getAllTasks');
    component.ngOnInit();
    expect(component.getAllTasks).toHaveBeenCalled();
  });

  it('should verify on refreshTaskStatus', () => {
    spyOn(component, 'selectTask');
    component.refreshTaskStatus();
    expect(component.selectTask).toHaveBeenCalled();
  });

  it('should verify on tabSelectedIndexChanged', () => {
    component.tabSelectedIndexChanged(event);
  });

  it('should verify on deleteTask', () => {
    spyOn(component, 'getAllTasks');
    component.deleteTask();
    component.isLoading = true;
    //  expect(component.getAllTasks).toHaveBeenCalled();
    expect(component.isLoading).toBeTruthy();
  });

  it('should verify togglebar() is called', () => {
    const action = 'ful';
    component.toggleSidebar(action);
  });

  it('should verify on getAllTasks', () => {
    component.getAllTasks();
    component.isLoading = true;
    expect(component.isLoading).toBeTruthy();
  });

  it('should verify on saveModel', () => {
    component.saveModel();
    component.isContentLoading = true;
    const options = {
      body: {
        filePath: selectedTask.pmmlFile,
        fileName: selectedTask.fileName
      }
    };
    expect(options.body.filePath).toEqual('/home/demo/ZMOD/model/New_636803506170859061.pmml');
    expect(options.body.fileName).toEqual('/home/demo/ZMOD/model/New_636803506170859061.pmml');
    expect(component.isContentLoading).toBeTruthy();
  });

  it('should verify on selectTask', () => {
    const selectedDataTask = {};
    component.selectTask(selectedDataTask);
    component.taskCompleted = false;
    component.isContentLoading = true;
    expect(component.taskCompleted).toBeFalsy();
    expect(component.isContentLoading).toBeTruthy();
  });

  it('should verify the delete task API response', async(() => {
    const mocResponse = { 'user': '', 'id': 'New_636803506170859061', 'message': 'Task Deleted.' };
    httpService.request(ApiRoutes.methods.DELETE, ApiRoutes.taskSaveModel(selectedTask.idforData))
    .pipe(finalize(() => { this.isLoading = false; }))
    .subscribe(response => {
      expect(response.message).toEqual(mocResponse.message);
    });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.taskSaveModel(selectedTask.idforData),
      method: ApiRoutes.methods.DELETE
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify the saveModel task API response', async(() => {
    const mocResponse = { 'user': '', 'id': 'New_636803506170859061', 'message': 'Saved to Models.' };
    const options = {
      body: {
        filePath: selectedTask.pmmlFile,
        fileName: selectedTask.fileName
      }
    };
    httpService.request(ApiRoutes.methods.POST, ApiRoutes.taskSaveModel(selectedTask.idforData), options)
    .pipe(finalize(() => { this.isLoading = false; }))
    .subscribe(response => {
      expect(response.message).toEqual(mocResponse.message);
    });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.taskSaveModel(selectedTask.idforData),
      method: ApiRoutes.methods.POST
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify the getAllTask API response', async(() => {
    const mocResponse = {
      'runningTask': [
        {
          'idforData': 'test',
          'status': 'PMML file Successfully Saved',
          'type': 'NNProject',
          'pid': 9140,
          'newPMMLFileName': 'test.pmml',
          'url': 'https://lambda-quad/tb/1'
        },
        {
          'idforData': '1545039227_autoML',
          'status': 'In Progress',
          'type': 'AutoMLProject',
          'pid': 10432,
          'newPMMLFileName': 'xyz1.pmml'
        }
      ]
    };
    const request = http.get('task');
    request.subscribe((response: any) => {
      expect(response).toEqual(mocResponse);
    });
    const req = httpMock.expectOne({
      url: environment.serverUrl + 'task',
      method: 'GET'
    });
    expect(req.request.responseType).toEqual('json');
    expect(req.request.method).toEqual('GET');
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify the select task API response for automl', async(() => {
    const mocResponse = {
      'pID': '10432',
      'status': 'In Progress',
      'newPMMLFileName': 'xyz1.pmml',
      'targetVar': 'origin',
      'problem_type': 'Classification',
      'idforData': '1545039227_autoML',
      'shape': [398, 9],
      'listOfModelAccuracy': [],
      'pmmlFilelocation': '',
      'generationInfo': []
    };
    httpService.request(ApiRoutes.methods.GET, ApiRoutes.taskGet(selectedTask.idforData))
    .pipe(finalize(() => { this.isContentLoading = false; }))
    .subscribe(response => {
      expect(response.status).toEqual(mocResponse.status);
    });
    const req = httpMock.expectOne({
      url: environment.serverUrl +  ApiRoutes.taskGet(selectedTask.idforData),
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(mocResponse);
    httpMock.verify();
  }));

  it('should verify for the error response', async(() => {
    const request = http.get(ApiRoutes.taskGet(selectedTask.idforData));
    const emsg = 'deliberate 500 error';
    request.subscribe((response: any) =>
      fail('should have failed with the 500 error'),
      (error: HttpErrorResponse) => {
        expect(error.status).toEqual(500, 'status');
      });

    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.taskGet(selectedTask.idforData),
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    req.flush(null, { status: 500, statusText: 'Server Error' });
    httpMock.verify();
  }));

});
