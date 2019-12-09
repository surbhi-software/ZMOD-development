import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { AppDropzoneComponent } from './dropzone.component';

describe('AppDropzoneComponent', () => {
  let component: AppDropzoneComponent;
  let fixture: ComponentFixture<AppDropzoneComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ AppDropzoneComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(AppDropzoneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
