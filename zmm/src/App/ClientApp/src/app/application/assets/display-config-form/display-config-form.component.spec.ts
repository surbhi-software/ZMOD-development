import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DisplayConfigFormComponent } from './display-config-form.component';

describe('DisplayConfigFormComponent', () => {
  let component: DisplayConfigFormComponent;
  let fixture: ComponentFixture<DisplayConfigFormComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DisplayConfigFormComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DisplayConfigFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
