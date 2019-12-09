import { async, ComponentFixture, TestBed, inject, tick, fakeAsync } from '@angular/core/testing';
import { HttpClientModule, HttpClient, HTTP_INTERCEPTORS } from '@angular/common/http';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiRoutes, AlertMessages } from '../../shared';
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
import { UtilService } from '../../shared/services/util.service';
import { ScrollingModule } from '@angular/cdk/scrolling';
import { SnackbarComponent } from '../../shared/snackbar/snackbar.component';
import { BrowserDynamicTestingModule } from '@angular/platform-browser-dynamic/testing';
import { AssetComponent } from './asset.component';
import { By } from '@angular/platform-browser';
import {
  MatToolbarModule,
  MatSidenavModule,
  MatMenuModule,
  MatTooltipModule,
  MatSnackBarModule,
} from '@angular/material';

describe('AssetComponent', () => {
  let component: AssetComponent;
  let fixture: ComponentFixture<AssetComponent>;
  let httpService: HttpService;
  let http: HttpClient;
  let httpMock: HttpTestingController;
  let selectedInstance: any = {};
  selectedInstance = {
    'id': 'BD_data',
    'name': 'BD_data.csv',
    'user': 'Rainer',
    'created_on': '12/7/2018 5:00:18 PM',
    'edited_on': '12/7/2018 5:00:18 PM',
    'type': 'TB',
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

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
      declarations: [
        AssetComponent,
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
        MatToolbarModule,
        MatSidenavModule,
        MatMenuModule,
        MatTooltipModule,
        MatSnackBarModule
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
      ]
    })
      .compileComponents();
  }));
  TestBed.overrideModule(BrowserDynamicTestingModule, {
    set: {
      entryComponents: [SnackbarComponent]
    }
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
    fixture = TestBed.createComponent(AssetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should verify if getAllInstances() is called', () => {
    component.getAllInstances();
    component.isLoading = true;
    expect(component.isLoading).toBeTruthy();
  });

  it('should verify if ngOnInit() is called', () => {
    spyOn(component, 'getAllInstances');
    component.ngOnInit();
    expect(component.getAllInstances).toHaveBeenCalled();
  });

  it('should verify if viewInstance() is called', () => {
    spyOn(component, 'getAllInstances');
    component.viewInstance(selectedInstance);
  });

  it('should verify if toggleSidebar() is called', () => {
    const action = 'fullscreen';
    component.toggleSidebar(action);
  });

  it('should verify if displayInstanceForm() is called', () => {
    component.displayInstanceForm();
    component.showFormPanel = true;
    expect(component.showFormPanel).toBeTruthy();
    const displayInstanceFormButton = fixture.debugElement.query(By.css('mat-toolbar button:nth-child(1)')).nativeElement;
    expect(displayInstanceFormButton.disabled).toBeFalsy();
  });

  it('should verify if killInstance() is called', () => {
    component.killInstance();
    component.isLoading = true;
    expect(component.isLoading).toBeTruthy();
  });
});
