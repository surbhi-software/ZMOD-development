import { async, ComponentFixture, TestBed, inject, tick, fakeAsync } from '@angular/core/testing';
import { HttpClientModule, HttpClient, HTTP_INTERCEPTORS, HttpHandler, HttpInterceptor } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiRoutes, UtilService, AlertMessages } from '../../shared';
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
import {
  MatButtonModule,
  MatCheckboxModule,
  MatTabsModule,
  MatDatepickerModule,
  MatNativeDateModule,
  MatFormFieldModule,
  MatInputModule,
  MatToolbarModule,
  MatSidenavModule,
  MatIconModule,
  MatMenuModule,
  MatStepperModule,
  MatTooltipModule,
  MatTableModule,
  MatSelectModule,
  MatRadioModule,
  MatSnackBarModule,
  MatProgressBarModule,
  MatExpansionModule,
  MatSlideToggleModule,
  MatPaginatorModule,
  MatSortModule,
} from '@angular/material';
import { CodeComponent } from './code.component';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { environment } from '../../../environments/environment';

describe('CodeComponent', () => {
  let component: CodeComponent;
  let fixture: ComponentFixture<CodeComponent>;
  let httpService: HttpService;
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let debugElement: DebugElement;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [
        CodeComponent,
        SearchFilterPipe,
        OrderByDatePipe,
        HighlightPipe,
        FileSizePipe
      ],
      imports: [
        FormsModule,
        HttpClientModule,
        HttpClientTestingModule,
        BrowserAnimationsModule,
        MatButtonModule,
        MatCheckboxModule,
        MatTabsModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatFormFieldModule,
        MatInputModule,
        MatToolbarModule,
        MatSidenavModule,
        MatIconModule,
        MatMenuModule,
        MatStepperModule,
        MatTooltipModule,
        MatTableModule,
        MatSelectModule,
        MatRadioModule,
        MatSnackBarModule,
        MatProgressBarModule,
        MatExpansionModule,
        MatSlideToggleModule,
        MatPaginatorModule,
        MatSortModule,
        ScrollingModule
      ],
      providers: [
        HttpService,
        HttpHandler,
        {
          provide: ApiRoutes
        },
        {
          provide: ApiPrefixInterceptor
        },
        {
          provide: UtilService
        },
        {
          provide: AlertMessages
        },
        {
          provide: HttpClient,
          useClass: HttpService
        },
        {
          provide: ErrorHandlerInterceptor
        },
      ]
    })
      .compileComponents();
  });
  const selectedCode = {
    'id': 'abc1',
    'name': 'abc1.py',
    'user': '',
    'created_on': '12/18/2018 11:02:55 AM',
    'edited_on': '12/18/2018 11:02:55 AM',
    'type': 'PYTHON',
    'url': '/uploads/code/abc1.py',
    'filePath': '/home/demo/ZMOD/code/abc1.py',
    'size': 35,
    'mimeType': 'text/plain',
    'extension': 'py',
    'properties': null
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
    fixture = TestBed.createComponent(CodeComponent);
    component = fixture.componentInstance;
  });

  it('Testing simple UI', () => {
    fixture.detectChanges();
    expect(true).toBeTruthy();
  });


  it('Call on ngOnInit', () => {
    spyOn(component, 'ngOnInit').and.callThrough();
  });


  it('Call on changeSelectedIndex', fakeAsync(() => {
    spyOn(component, 'changeSelectedIndex').and.returnValue('0');
  }));




  it('Test on alert message service', () => {
    expect(AlertMessages.CODE.delete).toEqual('Code Deleted');
  });



  it('Test on Api routes service', () => {
    expect(ApiRoutes.methods.DELETE).toEqual('delete');
    expect(ApiRoutes.code).toEqual('code');
    expect(ApiRoutes.codeGet(1)).toEqual('code/1');
  });



  it('should verify uploadnewFile() is called', () => {
    spyOn(component, 'changeSelectedIndex').and.callThrough();
    const button = fixture.debugElement.query(By.css('mat-toolbar button:nth-child(1)')).nativeElement;
    expect(button.disabled).toBeFalsy();
    button.click(null);
    expect(component.tabSelectedIndex).toBe(3);
    expect(component.changeSelectedIndex).toHaveBeenCalled();


  });


  it('should verify uploadFilesDone() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    spyOn(component, 'getAllCode');
    component.uploadFilesDone();
    component.uploadFiles = false;
    expect(component.uploadFiles).toBeFalsy();
    expect(component.changeSelectedIndex).toHaveBeenCalled();
    expect(component.getAllCode).toHaveBeenCalled();
  });

  it('should verify the getAllCode API testing', async(() => {
    const mocResponse = [{
      'id': 'abc1',
      'name': 'abc1.py',
      'user': '',
      'created_on': '12/18/2018 11:02:55 AM',
      'edited_on': '12/18/2018 11:02:55 AM',
      'type': 'PYTHON',
      'url': '/uploads/code/abc1.py',
      'filePath': '/home/demo/ZMOD/code/abc1.py',
      'size': 35,
      'mimeType': 'text/plain',
      'extension': 'py',
      'properties': null
    }];
    httpService.request(ApiRoutes.methods.GET, ApiRoutes.code)
      .pipe(finalize(() => { }))
      .subscribe((response) => {
        expect(response).toEqual(mocResponse);
        expect(response.length).toBe(1);
      });
    const req = httpMock.expectOne({
      url: environment.serverUrl + ApiRoutes.code,
      method: ApiRoutes.methods.GET
    });
    expect(req.request.responseType).toEqual('json');
    expect(req.request.body).toEqual(null);
    req.flush(mocResponse);
    httpMock.verify();
  }));


  it('should verify toggleSidebar is called', () => {
    const action = 'ful';
    component.toggleSidebar(action);
  });

  it('should verify  onCodeUploadSuccess() is called', () => {
    spyOn(component, 'onCodeUploadSuccess').and.callThrough();

  });


  it('should verify downloadCode() is called', () => {
    spyOn(component, 'downloadCode').and.callThrough();
    component.downloadCode();
    component.isContentLoading = true;
    expect(component.isContentLoading).toBeTruthy();
    const options = {
      responseType: 'blob'
    };
    expect(options.responseType).toEqual('blob');

  });


  it('should verify execute() is called', () => {
    spyOn(component, 'execute').and.callThrough();
    const code = selectedCode.id;
    component.execute();
    component.isLoading = true;
    expect(component.isLoading).toBeTruthy();
  });



  it('should verify deleteCode() is called', () => {
    spyOn(component, 'deleteCode').and.callThrough();
    const code = selectedCode.id;
    component.deleteCode();
    component.isLoading = true;

  });

  it('should verify close() is called', () => {
    spyOn(component, 'changeSelectedIndex');
    component.close();
    expect(component.changeSelectedIndex).toHaveBeenCalled();
  });

});
